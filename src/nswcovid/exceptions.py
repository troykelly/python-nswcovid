# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following lines in the
[options.entry_points] section in setup.cfg:

    console_scripts =
         fibonacci = nswcovid.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""


class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class MissingInformation(Error):
    """Exception raised if there is insufficient information to continue

    Attributes:
        message (str): explanation of the error
    """

    def __init__(self, message):
        super().__init__()
        self.message = message


class UnableToAuthenticate(Error):
    """Execption raised when the login process can not complete

    Attributes:
        message (str): explanation of the error
        status_code (int): the status code returned from the api
        response (object): Response object
    """

    def __init__(self, message, status_code=None, response=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.response = response


class NoSession(Error):
    """Execption raised when there is no existing API session

    Attributes:
        message (str): explanation of the error
    """

    def __init__(self, message):
        super().__init__()
        self.message = message


class CanNotRefresh(Error):
    """Execption raised when trying to refresh a token fails

    Attributes:
        message (str): explanation of the error
        response (object): Response object
    """

    def __init__(self, message, response=None):
        super().__init__()
        self.message = message
        self.response = response


class NSWCovidAPIError(Error):
    """Exception raised when transacting with the NSWCovid API

    Attributes:
        message (str): explanation of the error
        status_code (int): HTTP Status Code returned
        body (str): Message body
        json (object): Data returned
        headers (object): Response headers
        response (object): Response object
    """

    def __init__(
        self,
        message,
        status_code=None,
        body=None,
        json=None,
        headers=None,
        response=None,
    ):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.body = body
        self.json = json
        self.headers = headers
        self.response = response


class NSWCovidAccessDenied(Error):
    """Exception raised when permission is denied at the NSWCovid API

    Attributes:
        message (str): explanation of the error
        status_code (int): HTTP Status Code returned
        body (str): Message body
        json (object): Data returned
        headers (object): Response headers
        response (object): Response object
    """

    def __init__(
        self,
        message,
        status_code=None,
        body=None,
        json=None,
        headers=None,
        response=None,
    ):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.body = body
        self.json = json
        self.headers = headers
        self.response = response


class NSWCovidLoginFailed(Error):
    """Exception raised when unable to login to NSWCovid API

    Attributes:
        message (str): explanation of the error
        status_code (int): HTTP Status Code returned
        body (str): Message body
        json (object): Data returned
        headers (object): Response headers
        response (object): Response object
    """

    def __init__(
        self,
        message,
        status_code=None,
        body=None,
        json=None,
        headers=None,
        response=None,
    ):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.body = body
        self.json = json
        self.headers = headers
        self.response = response