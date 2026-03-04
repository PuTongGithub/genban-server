"""RSA非对称加密工具"""

import base64

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


class RsaUtil:
    # RSA加密工具类

    def __init__(self, private_key_content: str = "", public_key_content: str = ""):
        self.private_key = None
        self.public_key = None

        if private_key_content:
            self.private_key = RSA.import_key(private_key_content)

        if public_key_content:
            self.public_key = RSA.import_key(public_key_content)

    def decrypt(self, encrypted_data: str) -> str:
        # RSA私钥解密，输入Base64编码的密文，返回明文
        if not self.private_key:
            raise ValueError("私钥未加载")

        cipher = PKCS1_v1_5.new(self.private_key)
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted_bytes = cipher.decrypt(encrypted_bytes, None)
        if decrypted_bytes is None:
            raise ValueError("解密失败，返回数据为 None")
        return decrypted_bytes.decode("utf-8")

    def encrypt(self, plaintext: str) -> str:
        # RSA公钥加密，返回Base64编码的密文
        if not self.public_key:
            raise ValueError("公钥未加载")

        cipher = PKCS1_v1_5.new(self.public_key)
        encrypted_bytes = cipher.encrypt(plaintext.encode("utf-8"))
        return base64.b64encode(encrypted_bytes).decode("utf-8")


def generate_key_pair() -> tuple[str, str]:
    # 生成RSA密钥对，返回(私钥PEM, 公钥PEM)
    key = RSA.generate(2048)

    private_key = key.export_key().decode("utf-8")
    public_key = key.publickey().export_key().decode("utf-8")

    return private_key, public_key
