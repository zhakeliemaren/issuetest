import inspect
import functools
from typing import Optional, Mapping, Any, Union
from enum import Enum

import aiohttp
from aiohttp.typedefs import LooseHeaders, StrOrURL, JSONDecoder, DEFAULT_JSON_DECODER

from .log import LoggerFactory
from .config import ConfigsUtil
Logger = LoggerFactory.create_logger(
    name = '%s.rpc' % ConfigsUtil.get_obfastapi_config('log_name'),
    level = ConfigsUtil.get_obfastapi_config('log_level'),
    path = ConfigsUtil.get_obfastapi_config('log_path'),
    interval = ConfigsUtil.get_obfastapi_config('log_interval'),
    backup_count = ConfigsUtil.get_obfastapi_config('log_count')
)


__all__ = ("RPCResponse", "RPCService", "RPCServiceCenter")


def iscoroutinefunction_or_partial(obj: Any) -> bool:
    """
    Correctly determines if an object is a coroutine function,
    including those wrapped in functools.partial objects.
    """
    while isinstance(obj, functools.partial):
        obj = obj.func
    return inspect.iscoroutinefunction(obj)


DEFAULT_TIMEOUT = aiohttp.ClientTimeout(3 * 60)


class RPCResponse:

    def __init__(self, status_code: int, text: str):
        self.status_code = status_code
        self.text = text

    def json(self, loads: JSONDecoder = DEFAULT_JSON_DECODER) -> Any:
        stripped = self.text.strip()  # type: ignore
        if not stripped:
            return None

        return loads(stripped)


class RPCService:

    def __init__(self, host: str, headers: LooseHeaders={}):
        self._host = host
        self._headers = headers

    @property
    def host(self):
        return self._host

    @property
    def headers(self):
        return self._headers

    async def get(
            self, 
            url: StrOrURL,
            *, 
            params: Optional[Mapping[str, str]] = None,
            data: Any = None,
            json: Any = None,
            headers: Optional[LooseHeaders] = None,
            encoding: Optional[str] = None,
            timeout: Union[aiohttp.ClientTimeout, int] = DEFAULT_TIMEOUT,
            **kwargs
        ) -> RPCResponse:
        return await self.request("GET", url, params=params, data=data, json=json, headers=headers, encoding=encoding, timeout=timeout, **kwargs)

    async def options(
            self, 
            url: StrOrURL,
            *, 
            params: Optional[Mapping[str, str]] = None,
            data: Any = None,
            json: Any = None,
            headers: Optional[LooseHeaders] = None,
            encoding: Optional[str] = None,
            timeout: Union[aiohttp.ClientTimeout, int] = DEFAULT_TIMEOUT,
            **kwargs
        ) -> RPCResponse:
        return await self.request("OPTIONS", url, params=params, data=data, json=json, headers=headers, encoding=encoding, timeout=timeout, **kwargs)

    async def head(
            self, 
            url: StrOrURL,
            *, 
            params: Optional[Mapping[str, str]] = None,
            data: Any = None,
            json: Any = None,
            headers: Optional[LooseHeaders] = None,
            encoding: Optional[str] = None,
            timeout: Union[aiohttp.ClientTimeout, int] = DEFAULT_TIMEOUT,
            **kwargs
        ) -> RPCResponse:
        return await self.request("HEAD", url, params=params, data=data, json=json, headers=headers, encoding=encoding, timeout=timeout, **kwargs)

    async def post(
            self, 
            url: StrOrURL,
            *, 
            params: Optional[Mapping[str, str]] = None,
            data: Any = None,
            json: Any = None,
            headers: Optional[LooseHeaders] = None,
            encoding: Optional[str] = None,
            timeout: Union[aiohttp.ClientTimeout, int] = DEFAULT_TIMEOUT,
            **kwargs
        ) -> RPCResponse:
        return await self.request("POST", url, params=params, data=data, json=json, headers=headers, encoding=encoding, timeout=timeout, **kwargs)

    async def put(
            self, 
            url: StrOrURL,
            *, 
            params: Optional[Mapping[str, str]] = None,
            data: Any = None,
            json: Any = None,
            headers: Optional[LooseHeaders] = None,
            encoding: Optional[str] = None,
            timeout: Union[aiohttp.ClientTimeout, int] = DEFAULT_TIMEOUT,
            **kwargs
        ) -> RPCResponse:
        return await self.request("PUT", url, params=params, data=data, json=json, headers=headers, encoding=encoding, timeout=timeout, **kwargs)

    async def patch(
            self, 
            url: StrOrURL,
            *, 
            params: Optional[Mapping[str, str]] = None,
            data: Any = None,
            json: Any = None,
            headers: Optional[LooseHeaders] = None,
            encoding: Optional[str] = None,
            timeout: Union[aiohttp.ClientTimeout, int] = DEFAULT_TIMEOUT,
            **kwargs
        ) -> RPCResponse:
        return await self.request("PATCH", url, params=params, data=data, json=json, headers=headers, encoding=encoding, timeout=timeout, **kwargs)

    async def delete(
            self, 
            url: StrOrURL,
            *, 
            params: Optional[Mapping[str, str]] = None,
            data: Any = None,
            json: Any = None,
            headers: Optional[LooseHeaders] = None,
            encoding: Optional[str] = None,
            timeout: Union[aiohttp.ClientTimeout, int] = DEFAULT_TIMEOUT,
            **kwargs
        ) -> RPCResponse:
        return await self.request("DELETE", url, params=params, data=data, json=json, headers=headers, encoding=encoding, timeout=timeout, **kwargs)

    async def request(
            self,
            method: str,
            url: StrOrURL,
            *, 
            params: Optional[Mapping[str, str]] = None,
            data: Any = None,
            json: Any = None,
            headers: Optional[LooseHeaders] = None,
            encoding: Optional[str] = None,
            timeout: Union[aiohttp.ClientTimeout, int] = DEFAULT_TIMEOUT,
            **kwargs
        ) -> RPCResponse:
        if not url.startswith(self._host):
            url = "%s/%s" % (self._host, url)

        if headers:
            if self._headers:
                headers.update(self._headers)
        else:
            headers = self._headers

        if isinstance(timeout, int):
            timeout = aiohttp.ClientTimeout(total=timeout)
        
        Logger.debug('request %s params %s data %s json %s headers %s timeout %s' % (url, params, data, json, headers, timeout))
        async with aiohttp.request(method.upper(), url, params=params, data=data, json=json, headers=headers, timeout=timeout, **kwargs) as resp:
            text = await resp.text(encoding=encoding)
            Logger.debug('response code %s, text %s' % (resp.status, text))
            return RPCResponse(
                status_code=resp.status,
                text=text
            )


class RPCServiceError(Exception):
    pass


class RPCServiceCenter:

    _SERVICES = {}

    @classmethod
    def register(cls, name: str, *arg, **kwargs):
        """
        example:
            # register AService
            @RPCServiceCenter.register("service_a", host="http://127.1")
            class AService(RPCService):
                def get_host(self):
                    return self.host
        
        """
        def decorator(clz):
            if name not in cls._SERVICES:
                cls._SERVICES[name] = clz(*arg, **kwargs)
            else:
                raise RPCServiceError("'%s' is already registered by %s" % (name, cls._SERVICES[name].__class__))
    
            return clz

        return decorator

    @classmethod
    def call(cls, service_name: str, param_name: Optional[str]=None):
        """
        example:
            # example one: call AService
            @RPCServiceCenter.call("service_a")
            def call_aservice(service_a: AService):
                print (service_a.get_host())

            # example two: call AService
            @RPCServiceCenter.call("service_a", "a_service")
            def call_service_a(a_service: AService):
                print (a_service.get_host())
        params:
            service_name: service name registered in RPCServiceCenter
            param_name: name of service object in function
        """
        def decorator(func):
            def component(*arg, **kwargs):
                kwargs[param_name] = cls._SERVICES[service_name]
                return func(*arg, **kwargs)
            async def async_component(*arg, **kwargs):
                kwargs[param_name] = cls._SERVICES[service_name]
                return await func(*arg, **kwargs)

            if service_name not in cls._SERVICES:
                raise RPCServiceError("No such service '%s'" % service_name)

            return async_component if iscoroutinefunction_or_partial(func) else component

        if param_name is None:
            param_name = service_name

        return decorator
