from binascii import hexlify, unhexlify, a2b_hex
from pyDes import triple_des as td, PAD_PKCS5, CBC, ECB
from secrets import token_hex


class Output():

    def __init__(self):
        self.errors = []
        self.result = []

    def set_error(self, message):
        self.errors.append(message)

    def set_result(self, message):
        self.result.append(message)


class KeyConverter():

    def __init__(self, data=None):
        self.output = Output()
        self.parse_data(data)
        self.validate_data()

    def validate_data(self):
        if self.mk is None:
            self.output.set_error("Master Key mustn't be None")
        if self.mk is not None and not len(self.mk) == 32:
            self.output.set_error("Master Key must be 16 bytes or 32 chars")
        if self.ek is None:
            self.output.set_error("Encrypted Key mustn't be None")
        if self.ek is not None and not len(self.ek) in (32, 48):
            self.output.set_error("Encrypted Key must be 24 bytes (48 chars) "
                                  "or 16 bytes (32 chars)")
        if self.mode not in ('0', '1'):
            self.output.set_error("Mode must be 0 - ECB or 1 - CBC")
        if self.iv is None and self.mode == '1':
            self.output.set_error("IV must be inputed if CBC mode is chosen")
        if self.iv is not None and not len(self.iv) == 16:
            self.output.set_error("IV must be 8 bytes or 16 chars")

    def parse_data(self, data):
        self.mk = data.get('mk')
        self.ek = data.get('ek')
        self.mode = data.get('mode')
        self.iv = data.get('iv')

    def get_result(self):
        if len(self.output.errors) == 0:
            self.decrypt_ek_by_mk()
        return self.output

    def decrypt_ek_by_mk(self):
        ek, mk = unhexlify(self.ek), unhexlify(self.mk)
        iv = unhexlify(self.iv) if self.iv is not None else None
        k = td(mk, ECB) if self.mode == '0' else td(mk, CBC, iv)
        dk = k.decrypt(ek)
        dk = hexlify(dk).decode('utf-8').upper()
        self.output.set_result('Result decrypted key is %s' % dk)
