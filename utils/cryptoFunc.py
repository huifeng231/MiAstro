#!/usr/bin/env python
# encoding: utf-8
'''
@author: Mark li
@license: (C) Copyright 2013-2017, Node Supply Chain Manager Corporation Limited.
@contact: deamoncao100@gmail.com
@software: Pycharm
@file: cryptoFunc.py.py
@time: 2019-11-08 14:46
@desc:
'''


import hashlib

from Crypto.Cipher import DES, AES
import base64


mdes = DES.new(b'n(Kdwm&D', 1)


def decode_base64(text, platform=1):
    if not text: return text
    if platform == 2:
        dec_text = aes_func.decrypt(text)
    else:
        data = text.encode("utf-8")
        ret = mdes.decrypt(base64.decodebytes(data))
        padding_len = ret[-1]
        dec_text = ret[:-padding_len].decode("utf-8")
    return dec_text


def encrypt_base64(text):
    pad_len = 8 - len(text) % 8
    padding = chr(pad_len) * pad_len
    text += padding

    data = text.encode("utf-8")
    data = base64.encodebytes(mdes.encrypt(data))
    return data.decode("utf-8").replace('\n', '')


class PrpCrypt(object):
    """
    AES加密与解密
    """

    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC
        self.cipher_text = None

    def get_cryptor(self):
        sha384 = hashlib.sha384()
        sha384.update(self.key.encode('utf-8'))
        res = sha384.digest()

        crypt_or = AES.new(res[0:32], self.mode, res[32:48])

        return crypt_or

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):

        if not text:
            return text

        cryptor = self.get_cryptor()

        data = text.encode("utf-8")

        plain_text = cryptor.decrypt(base64.decodebytes(data))

        padding_len = plain_text[-1]

        plain_text = plain_text[:-padding_len].decode('utf-8')

        return plain_text

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):

        cryptor = self.get_cryptor()

        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + (chr(add) * add)

        data = text.encode('utf-8')
        print(cryptor.encrypt(data))
        data = base64.encodebytes(cryptor.encrypt(data))

        return data.decode('utf-8').replace('\n', '')


aes_func = PrpCrypt('fnd12)I&fnd12)I&')

if __name__ == '__main__':
    aa = encrypt_base64("{'a': '1', 'data': {'c_user': '100021780733863', 'dart': '_MS_XadKWWSbJOMIAh4nUkae', 'fr': '1Iv0ReW1hYCWKLcii.AWXHh9_XchPliTKRIRrWnq9JwJ0.Bdv8T8.oo.AAA.0.0.Bdv8o4.AWXaxXQ-', 'locale': 'zh_CN', 'noscript': '1', 'sb': '_MS_XWT-GCHjoQIBpAadRVK8', 'xs': '35%3AN3o73yHPuwiXrg%3A2%3A1572850232%3A2362%3A12591'}}")
    print(aa)
    enc_t = decode_base64("BhsJYsVi+11IbKsxlucLuMPl3J5JFylr2S7MptS22xVE5W3QGYtOchQwtxxsf3K9ZoJ3EgUPc7X3nm19woKO5xMtysOOFUvoRzhFOy1DhOgWmf4r5/GR1PciFdhuz1BUrGNg9nvXrJ4yAHAEsGxFzFd5mAQFOI6YRzEB8Y21Jh45wPxRFP6lB4jvlQFEJgKhKgNMe0sEqO69v/Hm2xZdnjtxVx3NqPgM/0oEUYgJIbwMsXMafCsz4CySik56ulu/iqJn/8Ye1ptOuDUAxQaAA159tlsdU2P+BmFtMJnrK6cSo1+bbifCisaaY7woMaofgIKrtATv5uZGVorG6suwUgV7qEgUPEroB2M04P2jiI5fl063om0/L8e/bfcaANFPXovSZDEU1oRMTgVwb5ADMQ2NXEXgwEAs")
    print(enc_t)
