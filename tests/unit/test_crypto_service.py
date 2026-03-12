"""CryptoService加密服务单元测试"""

import base64
import json

import pytest

from mijiaAPI_V2.infrastructure.crypto_service import CryptoService


class TestCryptoService:
    """CryptoService测试类"""

    def test_rc4_encrypt_decrypt_roundtrip(self):
        """测试RC4加密解密往返一致性"""
        # 准备测试数据
        original_data = b"Hello, World! This is a test message."
        key = b"test_key_12345"

        # 加密
        encrypted = CryptoService.rc4_encrypt(original_data, key)

        # 验证加密后数据不同
        assert encrypted != original_data

        # 解密
        decrypted = CryptoService.rc4_decrypt(encrypted, key)

        # 验证解密后数据与原始数据一致
        assert decrypted == original_data

    def test_rc4_encrypt_with_different_keys(self):
        """测试使用不同密钥加密产生不同结果"""
        data = b"test data"
        key1 = b"key1"
        key2 = b"key2"

        encrypted1 = CryptoService.rc4_encrypt(data, key1)
        encrypted2 = CryptoService.rc4_encrypt(data, key2)

        # 不同密钥应产生不同的加密结果
        assert encrypted1 != encrypted2

    def test_generate_nonce(self):
        """测试生成nonce"""
        nonce1 = CryptoService.generate_nonce()
        nonce2 = CryptoService.generate_nonce()

        # 验证nonce是Base64编码的字符串
        assert isinstance(nonce1, str)
        assert isinstance(nonce2, str)

        # 验证可以解码
        decoded1 = base64.b64decode(nonce1)
        decoded2 = base64.b64decode(nonce2)

        # 验证长度至少为12字节（8字节随机数 + 可变长度时间戳）
        assert len(decoded1) >= 12
        assert len(decoded2) >= 12

        # 验证两次生成的nonce不同（概率极高）
        assert nonce1 != nonce2

    def test_generate_signature(self):
        """测试生成签名"""
        uri = "/api/test"
        method = "POST"
        ssecurity = base64.b64encode(b"test_security_key").decode()
        nonce = CryptoService.generate_nonce()
        signed_nonce = CryptoService.get_signed_nonce(ssecurity, nonce)
        params = {"data": "test_data", "key": "value"}

        signature = CryptoService.generate_signature(uri, method, signed_nonce, params)

        # 验证签名是Base64编码的字符串
        assert isinstance(signature, str)

        # 验证可以解码
        decoded = base64.b64decode(signature)

        # SHA1签名长度为20字节
        assert len(decoded) == 20

    def test_encrypt_params(self):
        """测试加密请求参数"""
        # 准备测试数据
        uri = "/api/test"
        data = {"key1": "value1", "key2": 123, "key3": True}
        ssecurity = base64.b64encode(b"test_security_key").decode()

        # 加密参数
        result = CryptoService.encrypt_params(uri, data, ssecurity)

        # 验证返回结构
        assert "data" in result
        assert "_nonce" in result
        assert "signature" in result
        assert "ssecurity" in result
        assert "rc4_hash__" in result
        
        # 验证所有字段都是字符串
        assert isinstance(result["data"], str)
        assert isinstance(result["_nonce"], str)
        assert isinstance(result["signature"], str)
        assert isinstance(result["ssecurity"], str)
        assert isinstance(result["rc4_hash__"], str)

        # 验证可以解码加密数据
        encrypted_bytes = base64.b64decode(result["data"])
        nonce_bytes = base64.b64decode(result["_nonce"])

        assert len(encrypted_bytes) > 0
        assert len(nonce_bytes) >= 12

    def test_encrypt_params_with_empty_dict(self):
        """测试加密空字典"""
        uri = "/api/test"
        data = {}
        ssecurity = base64.b64encode(b"test_key").decode()

        result = CryptoService.encrypt_params(uri, data, ssecurity)

        assert "data" in result
        assert "_nonce" in result
        assert "signature" in result
        assert "ssecurity" in result

    def test_encrypt_params_with_complex_structure(self):
        """测试加密复杂数据结构"""
        uri = "/api/test"
        data = {
            "user": {"id": 123, "name": "测试用户"},
            "devices": [
                {"id": "device1", "status": "online"},
                {"id": "device2", "status": "offline"},
            ],
            "metadata": {"timestamp": 1234567890, "version": "1.0"},
        }
        ssecurity = base64.b64encode(b"complex_key").decode()

        result = CryptoService.encrypt_params(uri, data, ssecurity)

        # 验证返回结构完整
        assert "data" in result
        assert "_nonce" in result
        assert "signature" in result
        assert "ssecurity" in result
        assert "rc4_hash__" in result
