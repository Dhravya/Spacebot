"""asyncprawcore.sessions: Provides asyncprawcore.Session and asyncprawcore.session."""
import asyncio
import logging
import random
from copy import deepcopy
from urllib.parse import urljoin

from aiohttp.web import HTTPRequestTimeout

from .auth import BaseAuthorizer
from .codes import codes
from .const import TIMEOUT
from .exceptions import (
    BadJSON,
    BadRequest,
    Conflict,
    InvalidInvocation,
    NotFound,
    Redirect,
    RequestException,
    ServerError,
    SpecialError,
    TooLarge,
    TooManyRequests,
    UnavailableForLegalReasons,
    URITooLong,
)
from .rate_limit import RateLimiter
from .util import authorization_error_class

log = logging.getLogger(__package__)


class RetryStrategy(object):
    """An abstract class for scheduling request retries.

    The strategy controls both the number and frequency of retry attempts.

    Instances of this class are immutable.

    """

    async def sleep(self):
        """Sleep until we are ready to attempt the request."""
        sleep_seconds = self._sleep_seconds()
        if sleep_seconds is not None:
            message = f"Sleeping: {sleep_seconds:0.2f} seconds prior to retry"
            log.debug(message)
            await asyncio.sleep(sleep_seconds)


class FiniteRetryStrategy(RetryStrategy):
    """A ``RetryStrategy`` that retries requests a finite number of times."""

    def _sleep_seconds(self):
        if self._retries < 3:
            base = 0 if self._retries == 2 else 2
            return base + 2 * random.random()
        return None

    def __init__(self, retries=3):
        """Initialize the strategy.

        :param retries: Number of times to attempt a request.

        """
        self._retries = retries

    def consume_available_retry(self):
        """Allow one fewer retry."""
        return type(self)(self._retries - 1)

    def should_retry_on_failure(self):
        """Return ``True`` if and only if the strategy will allow another retry."""
        return self._retries > 1


class Session(object):
    """The low-level connection interface to reddit's API."""

    RETRY_EXCEPTIONS = (ConnectionError, HTTPRequestTimeout)
    RETRY_STATUSES = {
        520,
        522,
        codes["bad_gateway"],
        codes["gateway_timeout"],
        codes["internal_server_error"],
        codes["request_timeout"],
        codes["service_unavailable"],
    }
    STATUS_EXCEPTIONS = {
        codes["bad_gateway"]: ServerError,
        codes["bad_request"]: BadRequest,
        codes["conflict"]: Conflict,
        codes["found"]: Redirect,
        codes["forbidden"]: authorization_error_class,
        codes["gateway_timeout"]: ServerError,
        codes["internal_server_error"]: ServerError,
        codes["media_type"]: SpecialError,
        codes["moved_permanently"]: Redirect,
        codes["not_found"]: NotFound,
        codes["request_entity_too_large"]: TooLarge,
        codes["request_uri_too_large"]: URITooLong,
        codes["service_unavailable"]: ServerError,
        codes["too_many_requests"]: TooManyRequests,
        codes["unauthorized"]: authorization_error_class,
        codes["unavailable_for_legal_reasons"]: UnavailableForLegalReasons,
        520: ServerError,
        522: ServerError,
    }
    SUCCESS_STATUSES = {codes["accepted"], codes["created"], codes["ok"]}

    @staticmethod
    def _log_request(data, method, params, url):
        log.debug(f"Fetching: {method} {url}")
        log.debug(f"Data: {data}")
        log.debug(f"Params: {params}")

    @staticmethod
    def _preprocess_dict(data):
        new_data = {}
        for key, value in data.items():
            if isinstance(value, bool):
                new_data[key] = str(value).lower()
            elif value is not None:
                new_data[key] = str(value) if not isinstance(value, str) else value
        return new_data

    def __init__(self, authorizer):
        """Prepare the connection to reddit's API.

        :param authorizer: An instance of :class:`Authorizer`.

        """
        if not isinstance(authorizer, BaseAuthorizer):
            raise InvalidInvocation(f"invalid Authorizer: {authorizer}")
        self._authorizer = authorizer
        self._rate_limiter = RateLimiter()
        self._retry_strategy_class = FiniteRetryStrategy

    async def __aenter__(self):
        """Allow this object to be used as a context manager."""
        return self

    async def __aexit__(self, *_args):
        """Allow this object to be used as a context manager."""
        await self.close()

    async def _do_retry(
        self,
        data,
        json,
        method,
        params,
        response,
        retry_strategy_state,
        saved_exception,
        timeout,
        url,
    ):
        if saved_exception:
            status = repr(saved_exception)
        else:
            status = response.status
        log.warning(f"Retrying due to {status} status: {method} {url}")
        return await self._request_with_retries(
            data=data,
            json=json,
            method=method,
            params=params,
            timeout=timeout,
            url=url,
            retry_strategy_state=retry_strategy_state.consume_available_retry(),  # noqa: E501
        )

    async def _make_request(
        self,
        data,
        json,
        method,
        params,
        retry_strategy_state,
        timeout,
        url,
    ):
        try:
            response = await self._rate_limiter.call(
                self._requestor.request,
                self._set_header_callback,
                method,
                url,
                allow_redirects=False,
                data=data,
                json=json,
                params=params,
                timeout=timeout,
            )
            log.debug(
                f"Response: {response.status} ({response.headers.get('content-length')} bytes)"
            )
            return response, None
        except RequestException as exception:
            if (
                not retry_strategy_state.should_retry_on_failure()
                or not isinstance(  # noqa: E501
                    exception.original_exception, self.RETRY_EXCEPTIONS
                )
            ):
                raise
            return None, exception.original_exception

    def _preprocess_data(self, data, files):
        """Preprocess data and files before request.

        This is to convert requests that are formatted for the ``requests`` package to
        be compatible with the ``aiohttp`` package. The motivation for this is so that
        ``praw`` and ``asyncpraw`` can remain as similar as possible and thus making
        contributions to ``asyncpraw`` simpler.

        This method does the following:

        - Removes keys that have a value of ``None`` from ``data``.
        - Moves ``files`` into ``data``.

        :param data: Dictionary, bytes, or file-like object to send in the body of the
            request.
        :param files: Dictionary, mapping ``filename`` to file-like object to add to
            ``data``.

        """
        if isinstance(data, dict):
            data = self._preprocess_dict(data)
            if files is not None:
                data.update(files)
        return data

    def _preprocess_params(self, params):
        """Preprocess params before request.

        This is to convert requests that are formatted for the ``requests`` package to
        be compatible with ``aiohttp`` package. The motivation for this is so that
        ``praw`` and ``asyncpraw`` can remain as similar as possible and thus making
        contributions to ``asyncpraw`` simpler.

        This method does the following:

        - Removes keys that have a value of ``None`` from ``params``.
        - Casts bool values in ``params`` to str.

        :param params: The query parameters to send with the request.

        """
        return self._preprocess_dict(params)

    async def _request_with_retries(
        self,
        data,
        json,
        method,
        params,
        timeout,
        url,
        retry_strategy_state=None,
    ):
        if retry_strategy_state is None:
            retry_strategy_state = self._retry_strategy_class()

        await retry_strategy_state.sleep()
        self._log_request(data, method, params, url)
        response, saved_exception = await self._make_request(
            data,
            json,
            method,
            params,
            retry_strategy_state,
            timeout,
            url,
        )

        do_retry = False
        if response is not None and response.status == codes["unauthorized"]:
            self._authorizer._clear_access_token()
            if hasattr(self._authorizer, "refresh"):
                do_retry = True

        if retry_strategy_state.should_retry_on_failure() and (
            do_retry or response is None or response.status in self.RETRY_STATUSES
        ):
            return await self._do_retry(
                data,
                json,
                method,
                params,
                response,
                retry_strategy_state,
                saved_exception,
                timeout,
                url,
            )
        elif response.status in self.STATUS_EXCEPTIONS:
            if response.status == codes["media_type"]:
                # since exception class needs response.json
                raise self.STATUS_EXCEPTIONS[response.status](
                    response, await response.json()
                )
            else:
                raise self.STATUS_EXCEPTIONS[response.status](response)
        elif response.status == codes["no_content"]:
            return
        assert (
            response.status in self.SUCCESS_STATUSES
        ), f"Unexpected status code: {response.status}"
        if response.headers.get("content-length") == "0":
            return ""
        try:
            return await response.json()
        except ValueError:
            raise BadJSON(response)

    async def _set_header_callback(self):
        if not self._authorizer.is_valid() and hasattr(self._authorizer, "refresh"):
            await self._authorizer.refresh()
        return {"Authorization": f"bearer {self._authorizer.access_token}"}

    @property
    def _requestor(self):
        return self._authorizer._authenticator._requestor

    async def close(self):
        """Close the session and perform any clean up."""
        await self._requestor.close()

    async def request(
        self,
        method,
        path,
        data=None,
        files=None,
        json=None,
        params=None,
        timeout=TIMEOUT,
    ):
        """Return the json content from the resource at ``path``.

        :param method: The request verb. E.g., get, post, put.
        :param path: The path of the request. This path will be combined with the
            ``oauth_url`` of the Requestor.
        :param data: Dictionary, bytes, or file-like object to send in the body of the
            request.
        :param files: Dictionary, mapping ``filename`` to file-like object.
        :param json: Object to be serialized to JSON in the body of the request.
        :param params: The query parameters to send with the request.
        :param timeout: Specifies a particular timeout, in seconds.

        Automatically refreshes the access token if it becomes invalid and a refresh
        token is available. Raises InvalidInvocation in such a case if a refresh token
        is not available.

        """
        params = self._preprocess_params(deepcopy(params) or {})
        params["raw_json"] = 1
        if isinstance(data, dict):
            data = self._preprocess_data(deepcopy(data), files)
            data["api_type"] = "json"
            data = sorted(data.items())
        if isinstance(json, dict):
            json = deepcopy(json)
            json["api_type"] = "json"
        url = urljoin(self._requestor.oauth_url, path)
        return await self._request_with_retries(
            data=data,
            json=json,
            method=method,
            params=params,
            timeout=timeout,
            url=url,
        )


def session(authorizer=None):
    """Return a :class:`Session` instance.

    :param authorizer: An instance of :class:`Authorizer`.

    """
    return Session(authorizer=authorizer)
