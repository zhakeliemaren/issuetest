import sys
from typing_extensions import Self

from .log import LoggerFactory
from .config import ConfigsUtil, MysqlConfig

Logger = LoggerFactory.create_logger(
    name='sqlalchemy.engine',
    level=ConfigsUtil.get_obfastapi_config('log_level'),
    path=ConfigsUtil.get_obfastapi_config('log_path'),
    interval=ConfigsUtil.get_obfastapi_config('log_interval'),
    backup_count=ConfigsUtil.get_obfastapi_config('log_count')
)

from sqlalchemy.dialects.mysql.base import MySQLDialect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import DatabaseError

__all__ = ('aiomysql_session', 'AIOMysqlSessionMakerFactory', 'OBDataBaseError')
OBDataBaseError = DatabaseError


def _get_server_version_info(self, connection):
    # get database server version info explicitly over the wire
    # to avoid proxy servers like MaxScale getting in the
    # way with their own values, see #4205
    dbapi_con = connection.connection
    cursor = dbapi_con.cursor()
    cursor.execute("show global variables like 'version_comment'")
    val = cursor.fetchone()
    if val and 'OceanBase' in val[1]:
        val = '5.6.0'
    else:
        cursor.execute("SELECT VERSION()")
        val = cursor.fetchone()[0]
    cursor.close()
    from sqlalchemy import util
    if util.py3k and isinstance(val, bytes):
        val = val.decode()

    return self._parse_server_version(val)


setattr(MySQLDialect, '_get_server_version_info', _get_server_version_info)


class ConfigKey:

    def __init__(self, **config):
        check_sum = 0
        for key in config:
            check_sum += key.__hash__()
            check_sum += getattr(config[key], '__hash__', lambda: 0)()
        self.__hash = check_sum

    def __hash__(self):
        return self.__hash

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return value.__hash__() == self.__hash__()
        return False


class ORMAsyncExplicitTransactionHolder():

    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        await self.session.execute('BEGIN')

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            await self.session.commit()
        else:
            await self.session.rollback()
            raise exc_val


class ORMAsyncSession(AsyncSession, Session):

    async def __aenter__(self) -> Self:
        await super().__aenter__()
        return self

    def begin(self) -> ORMAsyncExplicitTransactionHolder:
        return ORMAsyncExplicitTransactionHolder(self)


class AIOMysqlSessionMakerFactory:
    _SESSIONS_MAKER = {}

    @classmethod
    def get_instance(cls, key: str, **kwargs) -> ORMAsyncSession:
        config = ConfigsUtil.get_mysql_config(key)
        config_key = ConfigKey(__config__=config, **kwargs)
        if config_key not in cls._SESSIONS_MAKER:
            cls._SESSIONS_MAKER[config_key] = cls.create_instance(config, **kwargs)
        return cls._SESSIONS_MAKER[config_key]

    @classmethod
    def create_instance(cls, config: MysqlConfig, **kwargs) -> ORMAsyncSession:
        engine = create_async_engine(config.get_url(), **kwargs)
        return sessionmaker(engine, autocommit=False, expire_on_commit=False, class_=ORMAsyncSession)


def aiomysql_session(
        key: str,
        max_overflow: int = 20,
        pool_size: int = 10,
        pool_timeout: int = 5,
        pool_recycle: int = 28800,
        echo: bool = False,
        **kwargs
) -> ORMAsyncSession:
    return AIOMysqlSessionMakerFactory.get_instance(
        key,
        max_overflow=max_overflow,
        pool_size=pool_size,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        echo=echo,
        **kwargs
    )()