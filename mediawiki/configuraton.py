from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional, Union

URL: str = "https://github.com/barrust/mediawiki"
VERSION: str = "0.7.4"


@dataclass
class Configuration:
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

    #  not in repr
    _reset_session: bool = field(default=True, init=False, repr=False)
    _clear_memoized: bool = field(default=False, init=False, repr=False)
    _rate_limit_last_call: Optional[datetime] = field(default=None, init=False, repr=False)
    _login: bool = field(default=False, init=False, repr=False)

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

    def __repr__(self):
        keys = [
            x.replace("_", "", 1)
            for x in sorted(self.__dataclass_fields__.keys())
            if x not in ["_login", "_rate_limit_last_call", "_clear_memoized", "_reset_session"]
        ]
        full = [f"{x}={self.__getattribute__(x)}" for x in keys]
        return f"Configuration({', '.join(full)})"

    @property
    def lang(self) -> str:
        return self._lang

    @lang.setter
    def lang(self, lang: str):
        print(f"lang setter: {lang}")
        t_lang = lang.lower()
        print(f"t_lang setter: {t_lang}")
        if self._lang == t_lang:
            print("non-change")
            return
        url = self._api_url
        tmp = url.replace(f"/{self._lang}.", f"/{t_lang}.")

        self.api_url = tmp
        self._lang = t_lang
        self._clear_memoized - True

    @property
    def api_url(self) -> str:
        return self._api_url

    @api_url.setter
    def api_url(self, api_url: str):
        self._lang = self.lang.lower()
        self._api_url = api_url.format(lang=self._lang)

        # reset session
        self._reset_session = True

    @property
    def category_prefix(self) -> str:
        return self._category_prefix

    @category_prefix.setter
    def category_prefix(self, category_prefix: str):
        self._category_prefix = category_prefix[:-1] if category_prefix[-1:] == ":" else category_prefix

    @property
    def user_agent(self) -> str:
        return self._user_agent

    @user_agent.setter
    def user_agent(self, user_agent: str):
        self._user_agent = user_agent

    @property
    def proxies(self) -> Optional[Dict]:
        return self._proxies

    @proxies.setter
    def proxies(self, proxies: Optional[Dict]):
        self._proxies = proxies if isinstance(proxies, dict) else None

        # reset session
        self._reset_session = True

    @property
    def verify_ssl(self) -> Union[bool, str]:
        return self._verify_ssl

    @verify_ssl.setter
    def verify_ssl(self, verify_ssl: Union[bool, str, None]):
        self._verify_ssl = verify_ssl if isinstance(verify_ssl, (bool, str)) else True

        # reset session
        self._reset_session = True

    @property
    def rate_limit(self) -> bool:
        return self._rate_limit

    @rate_limit.setter
    def rate_limit(self, rate_limit: bool):
        self._rate_limit = bool(rate_limit)
        self._rate_limit_last_call = None
        self._clear_memoized = True

    @property
    def rate_limit_min_wait(self) -> timedelta:
        return self._rate_limit_min_wait

    @rate_limit_min_wait.setter
    def rate_limit_min_wait(self, min_wait: timedelta):
        self._rate_limit_min_wait = min_wait
        self._rate_limit_last_call = None

    @property
    def username(self) -> Optional[str]:
        return self._username

    @username.setter
    def username(self, username: Optional[str]):
        self._username = username
        if self.username and self.password:
            self._login = True

    @property
    def password(self) -> Optional[str]:
        return self._password

    @password.setter
    def password(self, password: Optional[str]):
        self._password = password
        if self.username and self.password:
            self._login = True

    @property
    def refresh_interval(self) -> Optional[int]:
        return self._refresh_interval

    @refresh_interval.setter
    def refresh_interval(self, refresh_interval: Optional[int]):
        self._refresh_interval = (
            refresh_interval if isinstance(refresh_interval, int) and refresh_interval > 0 else None
        )

    @property
    def use_cache(self) -> bool:
        return self._use_cache

    @use_cache.setter
    def use_cache(self, use_cache: bool):
        self._use_cache = bool(use_cache)

    @property
    def timeout(self) -> Optional[float]:
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: Optional[float]):
        self._timeout = None if timeout is None else float(timeout)
