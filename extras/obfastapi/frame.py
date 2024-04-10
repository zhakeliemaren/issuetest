from .config import ConfigsUtil
from .log import LoggerFactory

import sys
import json
import base64
import threading
import importlib
import asyncio
import email.message
from uuid import uuid1, UUID
from inspect import isfunction, iscoroutinefunction
from enum import Enum
from typing import (
    Any,
    Callable,
    Coroutine,
    Generator,
    Dict,
    List,
    Tuple,
    Generic,
    TypeVar,
    Optional,
    Sequence,
    Set,
    Type,
    Union,
    cast
)

from pydantic import BaseModel
from pydantic.main import BaseConfig
from pydantic.fields import Undefined
from pydantic.schema import encode_default, ModelField, field_schema, model_process_schema
from pydantic.generics import GenericModel
from pydantic.typing import is_callable_type
from pydantic.utils import lenient_issubclass
from pydantic.error_wrappers import ErrorWrapper

from starlette.requests import Request
from starlette.datastructures import State, FormData
from starlette.middleware import Middleware
from starlette.exceptions import HTTPException
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse, Response
from starlette.status import *
from starlette.types import ASGIApp
from starlette.routing import request_response

from fastapi import FastAPI, APIRouter, Security
from fastapi.routing import BaseRoute, _prepare_response_content, APIRoute
from fastapi.params import Depends, Form
from fastapi.exceptions import RequestValidationError
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.utils import create_response_field
from fastapi.types import DecoratedCallable
from fastapi.security import APIKeyCookie
from starlette.background import BackgroundTasks
from starlette.websockets import WebSocket
from fastapi.security.oauth2 import SecurityScopes
from fastapi.dependencies.utils import (
    get_dependant,
    is_gen_callable,
    is_async_gen_callable,
    async_contextmanager_dependencies_error,
    solve_generator,
    is_coroutine_callable,
    request_body_to_args,
    request_params_to_args
)
from fastapi.dependencies.models import Dependant, SecurityRequirement
from fastapi.encoders import DictIntStrAny, SetIntStr, jsonable_encoder
from fastapi.openapi.utils import (
    Body,
    get_flat_models_from_routes,
    get_model_name_map,
    get_openapi_path
)
from fastapi.openapi.models import OpenAPI
from fastapi.openapi.constants import (
    METHODS_WITH_BODY,
    REF_PREFIX,
    STATUS_CODES_WITH_NO_BODY,
)

from .mysql import OBDataBaseError

Logger = LoggerFactory.create_logger(
    name='fastapi.logger',
    level=ConfigsUtil.get_obfastapi_config('log_level'),
    path=ConfigsUtil.get_obfastapi_config('log_path'),
    interval=ConfigsUtil.get_obfastapi_config('log_interval'),
    backup_count=ConfigsUtil.get_obfastapi_config('log_count')
)

__all__ = ("OBAPIRouter", "OBFastAPI", "OBResponse", "Controller", "DataList", "Trace", "Logger")


async def serialize_response(
        *,
        field: Optional[ModelField] = None,
        response_content: Any,
        include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
        exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
        by_alias: bool = True,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        is_coroutine: bool = True,
) -> Any:
    if field:
        errors = []
        if issubclass(type(response_content), BaseModel):
            value = response_content
        else:
            response_content = _prepare_response_content(
                response_content,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )
            if is_coroutine:
                value, errors_ = field.validate(response_content, {}, loc=("response",))
            else:
                value, errors_ = await run_in_threadpool(
                    field.validate, response_content, {}, loc=("response",)
                )
            if isinstance(errors_, ErrorWrapper):
                errors.append(errors_)
            elif isinstance(errors_, list):
                errors.extend(errors_)
        if errors:
            raise ValidationError(errors, field.type_)
        return jsonable_encoder(
            value,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )
    else:
        return jsonable_encoder(response_content)


async def solve_dependencies(
        *,
        request: Union[Request, WebSocket],
        dependant: Dependant,
        body: Optional[Union[Dict[str, Any], FormData]] = None,
        background_tasks: Optional[BackgroundTasks] = None,
        response: Optional[Response] = None,
        dependency_overrides_provider: Optional[Any] = None,
        dependency_cache: Optional[Dict[Tuple[Callable[..., Any], Tuple[str]], Any]] = None,
) -> Tuple[
    Dict[str, Any],
    List[ErrorWrapper],
    Optional[BackgroundTasks],
    Response,
    Dict[Tuple[Callable[..., Any], Tuple[str]], Any],
]:
    values: Dict[str, Any] = {}
    errors: List[ErrorWrapper] = []
    response = response or Response(
        content=None,
        status_code=200,  # type: ignore
        headers=None,  # type: ignore # in Starlette
        media_type=None,  # type: ignore # in Starlette
        background=None,  # type: ignore # in Starlette
    )
    dependency_cache = dependency_cache or {}
    sub_dependant: Dependant
    for sub_dependant in dependant.dependencies:
        sub_dependant.call = cast(Callable[..., Any], sub_dependant.call)
        sub_dependant.cache_key = cast(
            Tuple[Callable[..., Any], Tuple[str]], sub_dependant.cache_key
        )
        call = sub_dependant.call
        use_sub_dependant = sub_dependant
        if (
                dependency_overrides_provider
                and dependency_overrides_provider.dependency_overrides
        ):
            original_call = sub_dependant.call
            call = getattr(
                dependency_overrides_provider, "dependency_overrides", {}
            ).get(original_call, original_call)
            use_path: str = sub_dependant.path  # type: ignore
            use_sub_dependant = get_dependant(
                path=use_path,
                call=call,
                name=sub_dependant.name,
                security_scopes=sub_dependant.security_scopes,
            )
            use_sub_dependant.security_scopes = sub_dependant.security_scopes

        solved_result = await solve_dependencies(
            request=request,
            dependant=use_sub_dependant,
            body=body,
            background_tasks=background_tasks,
            response=response,
            dependency_overrides_provider=dependency_overrides_provider,
            dependency_cache=dependency_cache,
        )
        (
            sub_values,
            sub_errors,
            background_tasks,
            _,  # the subdependency returns the same response we have
            sub_dependency_cache,
        ) = solved_result
        dependency_cache.update(sub_dependency_cache)
        if sub_errors:
            errors.extend(sub_errors)
            continue
        if sub_dependant.use_cache and sub_dependant.cache_key in dependency_cache:
            solved = dependency_cache[sub_dependant.cache_key]
        elif is_gen_callable(call) or is_async_gen_callable(call):
            stack = request.scope.get("fastapi_astack")
            if stack is None:
                raise RuntimeError(
                    async_contextmanager_dependencies_error
                )  # pragma: no cover
            solved = await solve_generator(
                call=call, stack=stack, sub_values=sub_values
            )
        elif is_coroutine_callable(call):
            if isinstance(sub_dependant, OBDependant):
                solved = await call(__request__=request, **sub_values)
            else:
                solved = await call(**sub_values)
        else:
            if isinstance(sub_dependant, OBDependant):
                solved = await run_in_threadpool(call, __request__=request, **sub_values)
            else:
                solved = await run_in_threadpool(call, **sub_values)
        if sub_dependant.name is not None:
            values[sub_dependant.name] = solved
        if sub_dependant.cache_key not in dependency_cache:
            dependency_cache[sub_dependant.cache_key] = solved
    path_values, path_errors = request_params_to_args(
        dependant.path_params, request.path_params
    )
    query_values, query_errors = request_params_to_args(
        dependant.query_params, request.query_params
    )
    header_values, header_errors = request_params_to_args(
        dependant.header_params, request.headers
    )
    cookie_values, cookie_errors = request_params_to_args(
        dependant.cookie_params, request.cookies
    )
    values.update(path_values)
    values.update(query_values)
    values.update(header_values)
    values.update(cookie_values)
    errors += path_errors + query_errors + header_errors + cookie_errors
    if dependant.body_params:
        (
            body_values,
            body_errors,
        ) = await request_body_to_args(  # body_params checked above
            required_params=dependant.body_params, received_body=body
        )
        values.update(body_values)
        errors.extend(body_errors)
    if dependant.http_connection_param_name:
        values[dependant.http_connection_param_name] = request
    if dependant.request_param_name and isinstance(request, Request):
        values[dependant.request_param_name] = request
    elif dependant.websocket_param_name and isinstance(request, WebSocket):
        values[dependant.websocket_param_name] = request
    if dependant.background_tasks_param_name:
        if background_tasks is None:
            background_tasks = BackgroundTasks()
        values[dependant.background_tasks_param_name] = background_tasks
    if dependant.response_param_name:
        values[dependant.response_param_name] = response
    if dependant.security_scopes_param_name:
        values[dependant.security_scopes_param_name] = SecurityScopes(
            scopes=dependant.security_scopes
        )
    return values, errors, background_tasks, response, dependency_cache


def get_field_info_schema(field: ModelField) -> Tuple[Dict[str, Any], bool]:
    schema_overrides = False

    # If no title is explicitly set, we don't set title in the schema for enums.
    # The behaviour is the same as `BaseModel` reference, where the default title
    # is in the definitions part of the schema.
    schema: Dict[str, Any] = {}
    if field.field_info.title or not lenient_issubclass(field.type_, Enum):
        if field.field_info.title:
            schema['title'] = field.field_info.title
        else:
            # field.field_info.title =
            schema['title'] = field.name

    if field.field_info.title:
        schema_overrides = True

    if field.field_info.description:
        schema['description'] = field.field_info.description
        schema_overrides = True

    if (
            not field.required
            and not field.field_info.const
            and field.default is not None
            and not is_callable_type(field.outer_type_)
    ):
        schema['default'] = encode_default(field.default)
        schema_overrides = True

    return schema, schema_overrides


async def run_endpoint_function(
        *, request: Request, dependant: Dependant, values: Dict[str, Any], is_coroutine: bool
) -> Any:
    assert dependant.call is not None, "dependant.call must be a function"
    is_ob_dependant = isinstance(dependant, OBDependant)
    try:
        if is_ob_dependant:
            values['__request__'] = request
        if is_coroutine:
            return await dependant.call(**values)
        else:
            return await run_in_threadpool(dependant.call, **values)
    except OBDataBaseError as e:
        Logger.exception('Database Error')
        raise OBHTTPException(status_code=HTTP_400_BAD_REQUEST, msg='Database Error: %s' % e.orig)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        else:
            Logger.exception('INTERNAL SERVER ERROR')
            raise OBHTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, msg='INTERNAL SERVER ERROR')
    finally:
        if is_ob_dependant:
            dependant.clear_local(request)


def support_one_api(schema):
    if 'allOf' in schema and len(schema['allOf']) == 1:
        for ref in schema['allOf']:
            if ref.get('$ref'):
                schema['$ref'] = ref.get('$ref')
                break
    return schema


def get_model_definitions(
        *,
        flat_models: Set[Union[Type[BaseModel], Type[Enum]]],
        model_name_map: Dict[Union[Type[BaseModel], Type[Enum]], str],
) -> Dict[str, Any]:
    definitions: Dict[str, Dict[str, Any]] = {}
    for model in flat_models:
        m_schema, m_definitions, m_nested_models = model_process_schema(
            model, model_name_map=model_name_map, ref_prefix=REF_PREFIX
        )
        definitions.update(m_definitions)
        model_name = model_name_map[model]
        definitions[model_name] = m_schema
    for k in definitions:
        if 'properties' in definitions[k]:
            properties = definitions[k]['properties']
            for property_name in properties:
                support_one_api(properties[property_name])
    return definitions


def get_openapi_operation_request_body(
        *,
        body_field: Optional[ModelField],
        model_name_map: Dict[Union[Type[BaseModel], Type[Enum]], str],
) -> Optional[Dict[str, Any]]:
    if not body_field:
        return None
    assert isinstance(body_field, ModelField)
    body_schema, _, _ = field_schema(
        body_field, model_name_map=model_name_map, ref_prefix=REF_PREFIX
    )
    field_info = cast(Body, body_field.field_info)
    request_media_type = field_info.media_type
    required = body_field.required
    request_body_oai: Dict[str, Any] = {}
    if required:
        request_body_oai["required"] = required
    request_media_content: Dict[str, Any] = {"schema": support_one_api(body_schema)}
    if field_info.examples:
        request_media_content["examples"] = jsonable_encoder(field_info.examples)
    elif field_info.example != Undefined:
        request_media_content["example"] = jsonable_encoder(field_info.example)
    request_body_oai["content"] = {request_media_type: request_media_content}
    return request_body_oai


def get_openapi(
        *,
        title: str,
        version: str,
        openapi_version: str = "3.0.2",
        description: Optional[str] = None,
        routes: Sequence[BaseRoute],
        tags: Optional[List[Dict[str, Any]]] = None,
        servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
) -> Dict[str, Any]:
    info = {"title": title, "version": version}
    if description:
        info["description"] = description
    output: Dict[str, Any] = {"openapi": openapi_version, "info": info}
    if servers:
        output["servers"] = servers
    components: Dict[str, Dict[str, Any]] = {}
    paths: Dict[str, Dict[str, Any]] = {}
    flat_models = get_flat_models_from_routes(routes)
    model_name_map = get_model_name_map(flat_models)
    definitions = get_model_definitions(
        flat_models=flat_models, model_name_map=model_name_map
    )
    for route in routes:
        if isinstance(route, APIRoute):
            result = get_openapi_path(route=route, model_name_map=model_name_map)
            if result:
                path, security_schemes, _ = result
                if path:
                    paths.setdefault(route.path_format, {}).update(path)
                if security_schemes:
                    components.setdefault("securitySchemes", {}).update(
                        security_schemes
                    )
    if definitions:
        components["schemas"] = {k: definitions[k] for k in sorted(definitions)}
    if components:
        output["components"] = components
    output["paths"] = paths
    if tags:
        output["tags"] = tags
    return jsonable_encoder(OpenAPI(**output), by_alias=True, exclude_none=True)  # type: ignore


# 注入方法
setattr(sys.modules['fastapi.routing'], 'serialize_response', serialize_response)
setattr(sys.modules['fastapi.openapi.utils'], 'get_openapi_operation_request_body', get_openapi_operation_request_body)
# pydantic 升级后可能会失效
setattr(sys.modules['pydantic.schema'], 'get_field_info_schema', get_field_info_schema)

Data = TypeVar('Data')


class OBResponse(GenericModel, Generic[Data]):
    code: int = 200
    data: Optional[Data] = None
    msg: str = ''
    success: bool = True
    finished: bool = True


class DataList(GenericModel, Generic[Data]):
    total: int
    list: List[Data]


class Trace(BaseModel):
    trace_id: UUID

    def __init__(self, trace_id: Optional[UUID] = None):
        super().__init__(trace_id=trace_id if trace_id else uuid1())


class OBHTTPException(HTTPException):
    def __init__(
            self,
            status_code: int,
            msg: str = '',
            headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=msg)
        self.headers = headers


class ValidationError(BaseModel):
    loc: List[str]
    msg: str
    type: str


class HTTPValidationError(OBResponse):
    code: int = HTTP_422_UNPROCESSABLE_ENTITY
    data: List[ValidationError]


ob_http_exception_response_field = create_response_field(name='OBResponse', type_=OBResponse)
request_validation_exception_field = create_response_field(name='HTTPValidationError', type_=HTTPValidationError)


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        error['loc'] = list(error['loc'])
        errors.append(ValidationError(**error))
    response = HTTPValidationError(
        msg=str(exc),
        data=errors,
        success=False
    )
    response_data = await serialize_response(
        field=request_validation_exception_field,
        response_content=response,
    )
    return JSONResponse(response_data, status_code=response.code)


async def ob_http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    headers = getattr(exc, "headers", None)
    detail = OBResponse(code=exc.status_code, msg=exc.detail)
    response_data = await serialize_response(
        field=ob_http_exception_response_field,
        response_content=detail,
    )
    return JSONResponse(response_data, status_code=exc.status_code, headers=headers)


class User:

    def __init__(
            self,
            *,
            emp_id: Union[str, int] = '',
            name: str = '',
            nick: str = '',
            email: str = '',
            dept: str = ''
    ):
        self.emp_id: Union[str, int] = emp_id
        self.name: str = name
        self.nick: str = nick
        self.email: str = email
        self.dept: str = dept


class Controller:
    BUC_KEY_NAME = ConfigsUtil.get_obfastapi_config('buc_key')  # default OBVOS_USER_SIGN
    API_KEY_BUC_COOKIE = APIKeyCookie(name=BUC_KEY_NAME, auto_error=False)

    def __init__(self, user=None):
        self._user = user
        self._trace: Trace = Trace()

    def __hash__(self):
        return self.trace

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return value.__hash__() == self.__hash__()
        return False

    @property
    def user(self):
        return self._user

    @property
    def trace(self):
        return self._trace

    def b64_urlsafe_decode_with_padding(self, data: str) -> str:
        missing_padding = 4 - len(data) % 4
        if missing_padding:
            data += '=' * missing_padding
        return base64.urlsafe_b64decode(data)

    def get_user(
            self,
            cookie_key: str = Security(API_KEY_BUC_COOKIE)
    ):
        if cookie_key:
            try:
                payload_json = self.b64_urlsafe_decode_with_padding(cookie_key.split('.')[1])
                payload = json.loads(payload_json)
                user = payload.get('user')
                if user:
                    self._user = User(
                        emp_id=user.get('empId'),
                        name=user.get('loginName'),
                        nick=user.get('nickNameCn'),
                        email=user.get('emailAddr'),
                        dept=user.get('depDesc')
                    )
            except:
                pass
        if self._user:
            return self._user
        raise OBHTTPException(status_code=403, msg='Could not validate credentials')


class OBDependantLocal(Dict):
    pass


class OBRequestHanlder(object):

    def __init__(
            self,
            dependant: Dependant,
            body_field: Optional[ModelField] = None,
            status_code: int = 200,
            response_class: Union[Type[Response], DefaultPlaceholder] = Default(JSONResponse),
            response_field: Optional[ModelField] = None,
            response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            dependency_overrides_provider: Optional[Any] = None
    ) -> None:
        assert dependant.call is not None, "dependant.call must be a function"
        self.body_field = body_field
        self.is_coroutine = asyncio.iscoroutinefunction(dependant.call)
        self.is_body_form = body_field and isinstance(body_field.field_info, Form)
        if isinstance(response_class, DefaultPlaceholder):
            actual_response_class: Type[Response] = response_class.value
        else:
            actual_response_class = response_class
        self.dependant = dependant
        self.status_code = status_code
        self.dependency_overrides_provider = dependency_overrides_provider
        self.response_field = response_field
        self.response_model_include = response_model_include
        self.response_model_exclude = response_model_exclude
        self.response_model_by_alias = response_model_by_alias
        self.response_model_exclude_unset = response_model_exclude_unset
        self.response_model_exclude_defaults = response_model_exclude_defaults
        self.response_model_exclude_none = response_model_exclude_none
        self.actual_response_class = actual_response_class
        self.local_controllers_map: Dict[Request, OBDependantLocal] = {}

    def get_request_id(self, request):
        return id(request)

    def get_local_controllers(self, request: Request):
        request_id = self.get_request_id(request)
        if request_id not in self.local_controllers_map:
            self.local_controllers_map[request_id] = OBDependantLocal()
        return self.local_controllers_map[request_id]

    def free_local_controllers(self, request: Request):
        request_id = self.get_request_id(request)
        if request_id in self.local_controllers_map:
            del self.local_controllers_map[request_id]

    async def __call__(self, request: Request) -> Response:
        try:
            body: Any = None
            if self.body_field:
                if self.is_body_form:
                    body = await request.form()
                else:
                    body_bytes = await request.body()
                    if body_bytes:
                        json_body: Any = Undefined
                        content_type_value = request.headers.get("content-type")
                        if content_type_value:
                            message = email.message.Message()
                            message["content-type"] = content_type_value
                            if message.get_content_maintype() == "application":
                                subtype = message.get_content_subtype()
                                if subtype == "json" or subtype.endswith("+json"):
                                    json_body = await request.json()
                        if json_body != Undefined:
                            body = json_body
                        else:
                            body = body_bytes
        except json.JSONDecodeError as e:
            raise RequestValidationError([ErrorWrapper(e, ("body", e.pos))], body=e.doc)
        except Exception as e:
            raise OBHTTPException(
                status_code=400, msg="There was an error parsing the body"
            ) from e
        solved_result = await solve_dependencies(
            request=request,
            dependant=self.dependant,
            body=body,
            dependency_overrides_provider=self.dependency_overrides_provider,
        )
        values, errors, background_tasks, sub_response, _ = solved_result
        if errors:
            raise RequestValidationError(errors, body=body)
        else:
            raw_response = await run_endpoint_function(
                request=request, dependant=self.dependant, values=values, is_coroutine=self.is_coroutine
            )

            if isinstance(raw_response, Response):
                if raw_response.background is None:
                    raw_response.background = background_tasks
                return raw_response
            response_data = await serialize_response(
                field=self.response_field,
                response_content=raw_response,
                include=self.response_model_include,
                exclude=self.response_model_exclude,
                by_alias=self.response_model_by_alias,
                exclude_unset=self.response_model_exclude_unset,
                exclude_defaults=self.response_model_exclude_defaults,
                exclude_none=self.response_model_exclude_none,
                is_coroutine=self.is_coroutine,
            )
            response = self.actual_response_class(
                content=response_data,
                status_code=self.status_code,
                background=background_tasks,  # type: ignore # in Starlette
            )
            response.headers.raw.extend(sub_response.headers.raw)
            if sub_response.status_code:
                response.status_code = sub_response.status_code
            return response


class OBDependant(Dependant):

    def __init__(
            self,
            controller_cls: Type,
            *,
            request_handler: OBRequestHanlder = None,
            path_params: Optional[List[ModelField]] = None,
            query_params: Optional[List[ModelField]] = None,
            header_params: Optional[List[ModelField]] = None,
            cookie_params: Optional[List[ModelField]] = None,
            body_params: Optional[List[ModelField]] = None,
            dependencies: Optional[List["Dependant"]] = None,
            security_schemes: Optional[List[SecurityRequirement]] = None,
            name: Optional[str] = None,
            call: Optional[Callable[..., Any]] = None,
            request_param_name: Optional[str] = None,
            websocket_param_name: Optional[str] = None,
            http_connection_param_name: Optional[str] = None,
            response_param_name: Optional[str] = None,
            background_tasks_param_name: Optional[str] = None,
            security_scopes_param_name: Optional[str] = None,
            security_scopes: Optional[List[str]] = None,
            use_cache: bool = True,
            path: Optional[str] = None,
    ) -> None:
        if query_params:
            if query_params[0].name == 'self':
                del query_params[0]
                call = self._call(call)
        self.controller_cls: Type = controller_cls
        self.request_handler = request_handler
        super().__init__(path_params=path_params, query_params=query_params, header_params=header_params,
                         cookie_params=cookie_params, body_params=body_params, dependencies=dependencies,
                         security_schemes=security_schemes, name=name, call=call, request_param_name=request_param_name,
                         websocket_param_name=websocket_param_name,
                         http_connection_param_name=http_connection_param_name, response_param_name=response_param_name,
                         background_tasks_param_name=background_tasks_param_name,
                         security_scopes_param_name=security_scopes_param_name, security_scopes=security_scopes,
                         use_cache=use_cache, path=path)

    def get_controller(self, request: Request):
        # 避免依赖自身时重复创建导致self指针不一致
        if self.request_handler:
            local_controllers = self.request_handler.get_local_controllers(request)
            if self.controller_cls not in local_controllers:
                local_controllers[self.controller_cls] = self.controller_cls()
            return local_controllers[self.controller_cls]
        else:
            return self.controller_cls()

    def _call(self, endpoint: Optional[Callable[..., Any]]):
        if iscoroutinefunction(endpoint):
            async def __nt__(__request__: Request, *args, **kwargs):
                if not args or not isinstance(args[0], self.controller_cls):
                    args = list(args)
                    args.insert(0, self.get_controller(request=__request__))
                return await endpoint(*args, **kwargs)
        else:
            async def __nt__(__request__: Request, *args, **kwargs):
                if not args or not isinstance(args[0], self.controller_cls):
                    args = list(args)
                    args.insert(0, self.get_controller(request=__request__))
                return endpoint(*args, **kwargs)
        return __nt__

    def clear_local(self, request: Request):
        if self.request_handler:
            self.request_handler.free_local_controllers(request)


class OBAPIRoute(APIRoute):

    def __init__(
            self,
            path: str,
            endpoint: Callable[..., Any],
            *,
            response_model: Optional[Type[Any]] = None,
            status_code: int = 200,
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[Depends]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            response_description: str = "Successful Response",
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            deprecated: Optional[bool] = None,
            name: Optional[str] = None,
            methods: Optional[Union[Set[str], List[str]]] = None,
            operation_id: Optional[str] = None,
            response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            include_in_schema: bool = True,
            response_class: Union[Type[Response], DefaultPlaceholder] = Default(
                JSONResponse
            ),
            dependency_overrides_provider: Optional[Any] = None,
            callbacks: Optional[List[BaseRoute]] = None,
    ) -> None:
        super().__init__(path, endpoint, response_model=response_model, status_code=status_code, tags=tags,
                         dependencies=dependencies, summary=summary, description=description,
                         response_description=response_description, responses=responses, deprecated=deprecated,
                         name=name, methods=methods, operation_id=operation_id,
                         response_model_include=response_model_include, response_model_exclude=response_model_exclude,
                         response_model_by_alias=response_model_by_alias,
                         response_model_exclude_unset=response_model_exclude_unset,
                         response_model_exclude_defaults=response_model_exclude_defaults,
                         response_model_exclude_none=response_model_exclude_none, include_in_schema=include_in_schema,
                         response_class=response_class, dependency_overrides_provider=dependency_overrides_provider,
                         callbacks=callbacks)
        self.response_fields[HTTP_422_UNPROCESSABLE_ENTITY] = request_validation_exception_field
        threading.Thread(target=_init_controller, args=(self, self.request_hanlder)).start()

    def get_route_handler(self):
        self.request_hanlder = OBRequestHanlder(
            dependant=self.dependant,
            body_field=self.body_field,
            status_code=self.status_code,
            response_class=self.response_class,
            response_field=self.secure_cloned_response_field,
            response_model_include=self.response_model_include,
            response_model_exclude=self.response_model_exclude,
            response_model_by_alias=self.response_model_by_alias,
            response_model_exclude_unset=self.response_model_exclude_unset,
            response_model_exclude_defaults=self.response_model_exclude_defaults,
            response_model_exclude_none=self.response_model_exclude_none,
            dependency_overrides_provider=self.dependency_overrides_provider,
        )

        async def app(request: Request):
            return await self.request_hanlder(request)

        return app


class OBAPIRouter(APIRouter):

    def __init__(
            self,
            *,
            prefix: str = "",
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[Depends]] = None,
            default_response_class: Type[Response] = Default(JSONResponse),
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            callbacks: Optional[List[BaseRoute]] = None,
            routes: Optional[List[BaseRoute]] = None,
            redirect_slashes: bool = True,
            default: Optional[ASGIApp] = None,
            dependency_overrides_provider: Optional[Any] = None,
            route_class: Type[APIRoute] = OBAPIRoute,
            on_startup: Optional[Sequence[Callable[[], Any]]] = None,
            on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
            deprecated: Optional[bool] = None,
            include_in_schema: bool = True,
    ) -> None:
        super().__init__(prefix=prefix, tags=tags, dependencies=dependencies,
                         default_response_class=default_response_class, responses=responses, callbacks=callbacks,
                         routes=routes, redirect_slashes=redirect_slashes, default=default,
                         dependency_overrides_provider=dependency_overrides_provider, route_class=route_class,
                         on_startup=on_startup, on_shutdown=on_shutdown, deprecated=deprecated,
                         include_in_schema=include_in_schema)

    def api_route(
            self,
            path: str,
            *,
            response_model: Optional[Type[Any]] = None,
            status_code: int = 200,
            tags: Optional[List[str]] = None,
            dependencies: Optional[Sequence[Depends]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            response_description: str = "Successful Response",
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            deprecated: Optional[bool] = None,
            methods: Optional[List[str]] = None,
            operation_id: Optional[str] = None,
            response_model_include: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_exclude: Optional[Union[SetIntStr, DictIntStrAny]] = None,
            response_model_by_alias: bool = True,
            response_model_exclude_unset: bool = False,
            response_model_exclude_defaults: bool = False,
            response_model_exclude_none: bool = False,
            include_in_schema: bool = True,
            response_class: Type[Response] = Default(JSONResponse),
            name: Optional[str] = None,
            callbacks: Optional[List[BaseRoute]] = None,
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            self.add_api_route(
                path,
                func,
                response_model=response_model,
                status_code=status_code,
                tags=tags,
                dependencies=dependencies,
                summary=summary,
                description=description,
                response_description=response_description,
                responses=responses,
                deprecated=deprecated,
                methods=methods,
                operation_id=operation_id if operation_id else func.__name__,
                response_model_include=response_model_include,
                response_model_exclude=response_model_exclude,
                response_model_by_alias=response_model_by_alias,
                response_model_exclude_unset=response_model_exclude_unset,
                response_model_exclude_defaults=response_model_exclude_defaults,
                response_model_exclude_none=response_model_exclude_none,
                include_in_schema=include_in_schema,
                response_class=response_class,
                name=name,
                callbacks=callbacks,
            )
            return func

        return decorator


class OBFastAPI(FastAPI):

    def __init__(
            self,
            *,
            debug: bool = False,
            routes: Optional[List[OBAPIRouter]] = None,
            title: str = "FastAPI",
            description: str = "",
            version: str = "0.1.0",
            openapi_url: Optional[str] = "/openapi.json",
            openapi_tags: Optional[List[Dict[str, Any]]] = None,
            servers: Optional[List[Dict[str, Union[str, Any]]]] = None,
            dependencies: Optional[Sequence[Depends]] = None,
            default_response_class: Type[Response] = Default(JSONResponse),
            docs_url: Optional[str] = "/docs",
            redoc_url: Optional[str] = "/redoc",
            swagger_ui_oauth2_redirect_url: Optional[str] = "/docs/oauth2-redirect",
            swagger_ui_init_oauth: Optional[Dict[str, Any]] = None,
            middleware: Optional[Sequence[Middleware]] = None,
            exception_handlers: Optional[
                Dict[
                    Union[int, Type[Exception]],
                    Callable[[Request, Any], Coroutine[Any, Any, Response]],
                ]
            ] = None,
            on_startup: Optional[Sequence[Callable[[], Any]]] = None,
            on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
            root_prefix: str = "",
            openapi_prefix: str = "",
            root_path: str = "",
            root_path_in_servers: bool = True,
            responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
            callbacks: Optional[List[OBAPIRouter]] = None,
            deprecated: Optional[bool] = None,
            include_in_schema: bool = True,
            **extra: Any,
    ) -> None:
        self._debug: bool = debug
        self.state: State = State()
        self.router: OBAPIRouter = OBAPIRouter(
            routes=routes,
            prefix=root_prefix,
            dependency_overrides_provider=self,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            default_response_class=default_response_class,
            dependencies=dependencies,
            callbacks=callbacks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            responses=responses,
        )
        self.exception_handlers: Dict[
            Union[int, Type[Exception]],
            Callable[[Request, Any], Coroutine[Any, Any, Response]],
        ] = (
            {} if exception_handlers is None else dict(exception_handlers)
        )
        self.exception_handlers.setdefault(HTTPException, ob_http_exception_handler)
        self.exception_handlers.setdefault(
            RequestValidationError, request_validation_exception_handler
        )

        self.user_middleware: List[Middleware] = (
            [] if middleware is None else list(middleware)
        )
        self.middleware_stack: ASGIApp = self.build_middleware_stack()

        self.title = title
        self.description = description
        self.version = version
        self.servers = servers or []
        self.openapi_url = openapi_url
        self.openapi_tags = openapi_tags
        # TODO: remove when discarding the openapi_prefix parameter
        if openapi_prefix:
            Logger.warning(
                '"openapi_prefix" has been deprecated in favor of "root_path", which '
                "follows more closely the ASGI standard, is simpler, and more "
                "automatic. Check the docs at "
                "https://fastapi.tiangolo.com/advanced/sub-applications/"
            )
        self.root_path = root_path or openapi_prefix
        self.root_path_in_servers = root_path_in_servers
        self.docs_url = docs_url
        self.redoc_url = redoc_url
        self.swagger_ui_oauth2_redirect_url = swagger_ui_oauth2_redirect_url
        self.swagger_ui_init_oauth = swagger_ui_init_oauth
        self.extra = extra
        self.dependency_overrides: Dict[Callable[..., Any], Callable[..., Any]] = {}

        self.openapi_version = "3.0.2"

        if self.openapi_url:
            assert self.title, "A title must be provided for OpenAPI, e.g.: 'My API'"
            assert self.version, "A version must be provided for OpenAPI, e.g.: '2.1.0'"
        self.openapi_schema: Optional[Dict[str, Any]] = None
        self.setup()

    def openapi(self) -> Dict[str, Any]:
        if not self.openapi_schema:
            self.openapi_schema = get_openapi(
                title=self.title,
                version=self.version,
                openapi_version=self.openapi_version,
                description=self.description,
                routes=self.routes,
                tags=self.openapi_tags,
                servers=self.servers,
            )
        return self.openapi_schema


def _init_controller(route: OBAPIRoute, request_handler: OBRequestHanlder):
    import time
    while True:
        try:
            clz = route.endpoint.__qualname__.split('.')[0]
            mod = importlib.import_module(route.endpoint.__module__)
            clz = mod.__dict__[clz]
            break
        except:
            time.sleep(0.1)
    route.dependant = _clear_self(route.dependant, request_handler)
    route.app = request_response(route.get_route_handler())


def _clear_self(dependant: OBDependant, request_handler: OBRequestHanlder = None) -> OBDependant:
    endpoint = dependant.call
    if isfunction(endpoint) and '.' in endpoint.__qualname__:
        try:
            clz = endpoint.__qualname__.split('.')[0]
            mod = importlib.import_module(endpoint.__module__)
            clz = mod.__dict__[clz]
            if issubclass(clz, Controller):
                dependant = OBDependant(
                    clz,
                    request_handler=request_handler,
                    path_params=dependant.path_params,
                    query_params=dependant.query_params,
                    header_params=dependant.header_params,
                    cookie_params=dependant.cookie_params,
                    body_params=dependant.body_params,
                    dependencies=dependant.dependencies,
                    security_schemes=dependant.security_requirements,
                    name=dependant.name,
                    call=dependant.call,
                    request_param_name=dependant.request_param_name,
                    http_connection_param_name=dependant.http_connection_param_name,
                    response_param_name=dependant.response_param_name,
                    websocket_param_name=dependant.websocket_param_name,
                    background_tasks_param_name=dependant.background_tasks_param_name,
                    security_scopes_param_name=dependant.security_scopes_param_name,
                    security_scopes=dependant.security_scopes,
                    use_cache=dependant.use_cache,
                    path=dependant.path
                )
        except:
            Logger.exception("Fail to init Dependant")

    if dependant.dependencies:
        dependant.dependencies = [_clear_self(d, request_handler) for d in dependant.dependencies]
    return dependant
