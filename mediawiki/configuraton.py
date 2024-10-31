"""Configuration module"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Tuple, Union

URL: str = "https://github.com/barrust/mediawiki"
VERSION: str = "0.7.5"

HTTPAuthenticator = Union[Tuple[str, str], Callable[[Any], Any]]


@dataclass
class Configuration:
    """Configuration class"""

    _lang: str = field(default="en", init=False, repr=False)
    _api_url: str = field(default="https://en.wikipedia.org/w/api.php", init=False, repr=False)
    _category_prefix: str = field(default="Category", init=False, repr=False)
    _timeout: Optional[float] = field(default=15.0, init=False, repr=False)
    _user_agent: str = field(default=f"python-mediawiki/VERSION-{VERSION}/({URL})/BOT", init=False, repr=False)
    _proxies: Optional[Dict] = field(default=None, init=False, repr=False)
    _verify_ssl: Union[bool, str] = field(default=True, init=False, repr=False)
    _rate_limit: bool = field(default=False, init=False, repr=False)
    _rate_limit_min_wait: timedelta = field(default=timedelta(milliseconds=50), init=False, repr=False)
    _username: Optional[str] = field(default=None, init=False, repr=False)
    _password: Optional[str] = field(default=None, init=False, repr=False)
    _refresh_interval: Optional[int] = field(default=None, init=False, repr=False)
    _use_cache: bool = field(default=True, init=False, repr=False)
    _http_auth: Optional[HTTPAuthenticator] = field(default=None, init=False, repr=False)

    #  not in repr
    _reset_session: bool = field(default=True, init=False, repr=False)
    _clear_memoized: bool = field(default=False, init=False, repr=False)
    _rate_limit_last_call: Optional[datetime] = field(default=None, init=False, repr=False)

    def __init__(
        self,
        lang: Optional[str] = None,
        api_url: Optional[str] = None,
        category_prefix: Optional[str] = None,
        timeout: Optional[float] = None,
        user_agent: Optional[str] = None,
        proxies: Optional[Dict] = None,
        verify_ssl: Union[bool, str, None] = None,
        rate_limit: bool = False,
        rate_limit_wait: Optional[timedelta] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        refresh_interval: Optional[int] = None,
        use_cache: bool = True,
        http_auth: Optional[HTTPAuthenticator] = None,
    ):
        if api_url:
            self._api_url = api_url

        if lang:
            self.lang = lang

        if category_prefix:
            self.category_prefix = category_prefix

        if user_agent:
            self._user_agent = user_agent

        if proxies:
            self.proxies = proxies

        if verify_ssl:
            self.verify_ssl = verify_ssl

        if rate_limit:
            self.rate_limit = rate_limit

        if rate_limit_wait:
            self._rate_limit_min_wait = rate_limit_wait

        if username:
            self.username = username

        if password:
            self.password = password

        if refresh_interval:
            self.refresh_interval = refresh_interval

        if use_cache:
            self.use_cache = use_cache

        if timeout:
            self.timeout = timeout

        if http_auth:
            self.http_auth = http_auth

    def __repr__(self):
        """repr"""
        keys = [
            x.replace("_", "", 1)
            for x in sorted(asdict(self).keys())
            if x not in ["_rate_limit_last_call", "_clear_memoized", "_reset_session"]
        ]
        full = [f"{x}={self.__getattribute__(x)}" for x in keys]
        return f"Configuration({', '.join(full)})"

    @property
    def lang(self) -> str:
        """str: The API URL language, if possible this will update the API URL

        Note:
            Use correct language titles with the updated API URL
        Note:
            Some API URLs do not encode language; unable to update if this is the case"""
        return self._lang

    @lang.setter
    def lang(self, language: str):
        """Set the language to use; attempts to change the API URL"""
        if self._lang == language.lower():
            return
        url = self._api_url
        tmp = url.replace(f"/{self._lang}.", f"/{language.lower()}.")

        self.api_url = tmp
        self._lang = language.lower()
        self._clear_memoized = True

    @property
    def api_url(self) -> str:
        """str: API URL of the MediaWiki site

        Note:
            Not settable; See :py:func:`mediawiki.MediaWiki.set_api_url`"""
        return self._api_url

    @api_url.setter
    def api_url(self, api_url: str):
        self._lang = self.lang.lower()
        self._api_url = api_url.format(lang=self._lang)

        # reset session
        self._reset_session = True

    @property
    def category_prefix(self) -> str:
        """str: The category prefix to use when using category based functions

        Note:
            Use the correct category name for the language selected"""
        return self._category_prefix

    @category_prefix.setter
    def category_prefix(self, category_prefix: str):
        """Set the category prefix correctly"""
        self._category_prefix = category_prefix[:-1] if category_prefix[-1:] == ":" else category_prefix

    @property
    def user_agent(self) -> str:
        """str: User agent string

        Note:
            If using in as part of another project, this should be changed"""
        return self._user_agent

    @user_agent.setter
    def user_agent(self, user_agent: str):
        """Set the new user agent string

        Note:
            Will need to re-log into the MediaWiki if user agent string is changed"""
        self._user_agent = user_agent

    @property
    def proxies(self) -> Optional[Dict]:
        """dict: Turn on, off, or set proxy use with the Requests library"""
        return self._proxies

    @proxies.setter
    def proxies(self, proxies: Optional[Dict]):
        """Turn on, off, or set proxy use through the Requests library"""
        self._proxies = proxies if isinstance(proxies, dict) else None

        # reset session
        self._reset_session = True

    @property
    def verify_ssl(self) -> Union[bool, str]:
        """bool | str: Verify SSL when using requests or path to cert file"""
        return self._verify_ssl

    @verify_ssl.setter
    def verify_ssl(self, verify_ssl: Union[bool, str, None]):
        """Set request verify SSL parameter; defaults to True if issue"""
        self._verify_ssl = verify_ssl if isinstance(verify_ssl, (bool, str)) else True

        # reset session
        self._reset_session = True

    @property
    def rate_limit(self) -> bool:
        """bool: Turn on or off Rate Limiting"""
        return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, rate_limit: bool):
        """Turn on or off rate limiting"""
        self._rate_limit = bool(rate_limit)
        self._rate_limit_last_call = None
        self._clear_memoized = True

    @property
    def rate_limit_min_wait(self) -> timedelta:
        """timedelta: Time to wait between calls

        Note:
            Only used if rate_limit is **True**"""
        return self._rate_limit_min_wait

    @rate_limit_min_wait.setter
    def rate_limit_min_wait(self, min_wait: timedelta):
        """Set minimum wait to use for rate limiting"""
        self._rate_limit_min_wait = min_wait
        self._rate_limit_last_call = None

    @property
    def username(self) -> Optional[str]:
        """str | None: Username to use to log into the mediawiki site"""
        return self._username

    @username.setter
    def username(self, username: Optional[str]):
        """set the username, if needed, to log into the mediawiki site"""
        self._username = username

    @property
    def password(self) -> Optional[str]:
        """str | None: Password to use to log into the mediawiki site"""
        return self._password

    @password.setter
    def password(self, password: Optional[str]):
        """set the password, if needed, to log into the mediawiki site"""
        self._password = password

    @property
    def refresh_interval(self) -> Optional[int]:
        """int | None: The interval at which the memoize cache is to be refresh"""
        return self._refresh_interval

    @refresh_interval.setter
    def refresh_interval(self, refresh_interval: Optional[int]):
        "Set the new cache refresh interval" ""
        self._refresh_interval = (
            refresh_interval if isinstance(refresh_interval, int) and refresh_interval > 0 else None
        )

    @property
    def use_cache(self) -> bool:
        """bool: Whether caching should be used; on (**True**) or off (**False**)"""
        return self._use_cache

    @use_cache.setter
    def use_cache(self, use_cache: bool):
        """toggle using the cache or not"""
        self._use_cache = bool(use_cache)

    @property
    def timeout(self) -> Optional[float]:
        """float: Response timeout for API requests

        Note:
            Use **None** for no response timeout"""
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: Optional[float]):
        """Set request timeout in seconds (or fractions of a second)"""
        self._timeout = None if timeout is None else float(timeout)

    @property
    def http_auth(self) -> Optional[HTTPAuthenticator]:
        """tuple|callable: HTTP authenticator to use to access the mediawiki site"""
        return self._http_auth

    @http_auth.setter
    def http_auth(self, http_auth: Optional[HTTPAuthenticator]):
        """Set the HTTP authenticator, if needed, to use to access the mediawiki site"""
        self._http_auth = http_auth
