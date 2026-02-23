class UsernameOrEmailAlreadyExists(Exception):
    pass


class UsernameAlreadyExists(Exception):
    pass


class EmailAlreadyExists(Exception):
    pass


class IncorrectPasswordOrUsername(Exception):
    pass


class InsufficientPermission(Exception):
    pass


class InvalidRefreshToken(Exception):
    pass
