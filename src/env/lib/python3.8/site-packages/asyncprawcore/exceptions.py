"""Provide exception classes for the asyncprawcore package."""

from urllib.parse import urlparse


class AsyncPrawcoreException(Exception):
    """Base exception class for exceptions that occur within this package."""


class InvalidInvocation(AsyncPrawcoreException):
    """Indicate that the code to execute cannot be completed."""


class RequestException(AsyncPrawcoreException):
    """Indicate that there was an error with the incomplete HTTP request."""

    def __init__(self, original_exception, request_args, request_kwargs):
        """Initialize a RequestException instance.

        :param original_exception: The original exception that occurred.
        :param request_args: The arguments to the request function.
        :param request_kwargs: The keyword arguments to the request function.

        """
        self.original_exception = original_exception
        self.request_args = request_args
        self.request_kwargs = request_kwargs
        super(RequestException, self).__init__(
            f"error with request {original_exception}"
        )


class ResponseException(AsyncPrawcoreException):
    """Indicate that there was an error with the completed HTTP request."""

    def __init__(self, response):
        """Initialize a ResponseException instance.

        :param response: The response returned from an aiohttp request.

        """
        self.response = response
        super(ResponseException, self).__init__(
            f"received {response.status} HTTP response"
        )


class OAuthException(AsyncPrawcoreException):
    """Indicate that there was an OAuth2 related error with the request."""

    def __init__(self, response, error, description):
        """Intialize a OAuthException instance.

        :param response: The response returned from an aiohttp request.
        :param error: The error type returned by reddit.
        :param description: A description of the error when provided.

        """
        self.error = error
        self.description = description
        self.response = response
        message = f"{error} error processing request"
        if description:
            message += f" ({description})"
        AsyncPrawcoreException.__init__(self, message)


class BadJSON(ResponseException):
    """Indicate the response did not contain valid JSON."""


class BadRequest(ResponseException):
    """Indicate invalid parameters for the request."""


class Conflict(ResponseException):
    """Indicate a conflicting change in the target resource."""


class Forbidden(ResponseException):
    """Indicate the authentication is not permitted for the request."""


class InsufficientScope(ResponseException):
    """Indicate that the request requires a different scope."""


class InvalidToken(ResponseException):
    """Indicate that the request used an invalid access token."""


class NotFound(ResponseException):
    """Indicate that the requested URL was not found."""


class Redirect(ResponseException):
    """Indicate the request resulted in a redirect.

    This class adds the attribute ``path``, which is the path to which the response
    redirects.

    """

    def __init__(self, response):
        """Initialize a Redirect exception instance.

        :param response: The response returned from an aiohttp request.

        """
        path = urlparse(response.headers.get("location")).path
        self.path = path[:-5] if path.endswith(".json") else path
        self.response = response
        msg = f"Redirect to {self.path}"
        msg += (
            " (You may be trying to perform a non-read-only action via a "
            "read-only instance.)"
            if "/login/" in self.path
            else ""
        )
        AsyncPrawcoreException.__init__(self, msg)


class ServerError(ResponseException):
    """Indicate issues on the server end preventing request fulfillment."""


class SpecialError(ResponseException):
    """Indicate syntax or spam-prevention issues."""

    def __init__(self, response, resp_dict):
        """Initialize a SpecialError exception instance.

        :param response: The response returned from an aiohttp request.

        """
        self.response = response

        self.message = resp_dict.get("message", "")
        self.reason = resp_dict.get("reason", "")
        self.special_errors = resp_dict.get("special_errors", [])
        AsyncPrawcoreException.__init__(self, f"Special error {self.message!r}")


class TooLarge(ResponseException):
    """Indicate that the request data exceeds the allowed limit."""


class TooManyRequests(ResponseException):
    """Indicate that the user has sent too many requests in a given amount of time."""

    def __init__(self, response):
        """Initialize a TooManyRequests exception instance.

        :param response: A requests.response instance that may contain a retry-after
            header and a message.

        """
        self.response = response
        self.retry_after = response.headers.get("retry-after")
        self.message = response.text  # Not all response bodies are valid JSON

        msg = f"received {response.status} HTTP response"
        if self.retry_after:
            msg += (
                f". Please wait at least {float(self.retry_after)} seconds "
                "before re-trying this request."
            )
        AsyncPrawcoreException.__init__(self, msg)


class UnavailableForLegalReasons(ResponseException):
    """Indicate that the requested URL is unavailable due to legal reasons."""


class URITooLong(ResponseException):
    """Indicate that the length of the request URI exceeds the allowed limit."""
