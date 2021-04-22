import ed25519


class Account(object):
    """用户对象"""
    def __init__(self):
        self.signing_key, self.verifying_key = ed25519.create_keypair()
        self.PublicKey = self.verifying_key.to_ascii(encoding="hex")
        self.PrivateKey = self.signing_key.to_ascii(encoding="hex")
        self.SigningKey = self.signing_key
        self.VerifiyingKey = self.verifying_key
        self.Username = str(self.PublicKey)[2:-1]
        self.Password = str(self.PrivateKey)[2:-1]

    def create_account(self):
        return self.Username, self.Password


if __name__ == "__main__":
    print(Account().create_account())
    pass

