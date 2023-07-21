class CustomError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class PrivateAccountError(CustomError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class NoPostError(CustomError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class NoAccountError(CustomError):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg
