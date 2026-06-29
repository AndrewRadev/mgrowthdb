class LoginRequired(Exception):
    "Exception raised by handlers to request a redirect to the login page"
    pass


class ClientError(Exception):
    "Exception raised by JSON handlers that is meant to be rendered with a status 400"
    pass
