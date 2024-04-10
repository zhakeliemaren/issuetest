from typing import Union, Dict, Any
from urllib import parse


__all__ = ["ConfigsUtil", "MysqlConfig"]


class ConfigsError(Exception):
    pass


class Config:

    def __hash__(self):
        check_sum = 0
        config = self.__dict__
        for key in config:
            check_sum += key.__hash__()
            check_sum += getattr(config[key], '__hash__', lambda:0)()
        return check_sum

    def __eq__(self, value):
        if isinstance(value, self.__class__):
            return value.__hash__() == self.__hash__()
        return False


class MysqlConfig(Config):

    def __init__(self, host: str, port: int, dbname: str, user: str, passwd: str=None):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.passwd = passwd

    def get_url(self, drive: str="aiomysql", charset='utf8'):
        user = parse.quote_plus(self.user)
        if self.passwd:
            user = '%s:%s' % (user, parse.quote_plus(self.passwd))

        url = "mysql+%s://%s@%s:%s/%s" % (drive, user, self.host, self.port, self.dbname)

        if charset:
            url += "?charset=%s" % charset
        return url


class RedisConfig(Config):

    def __init__(
        self, 
        host: str,
        *,
        port: int = 6379,
        db: Union[str, int] = 0,
        password: str = None,
        socket_timeout: float = None,
        socket_connect_timeout: float = None,
        socket_keepalive: bool = None,
        socket_keepalive_options: Dict[str, Any] = None,
        unix_socket_path: str = None,
        encoding: str = "utf-8",
        encoding_errors: str = "strict",
        decode_responses: bool = False,
        retry_on_timeout: bool = False,
        ssl: bool = False,
        ssl_keyfile: str = None,
        ssl_certfile: str = None,
        ssl_cert_reqs: str = "required",
        ssl_ca_certs: str = None,
        ssl_check_hostname: bool = False,
        max_connections: int = 0,
        single_connection_client: bool = False,
        health_check_interval: int = 0,
        client_name: str = None,
        username: str = None
        ):
        self.host: str = host
        self.port: int = port
        self.db: Union[str, int] = db
        self.password: str = password
        self.socket_timeout: float = socket_timeout
        self.socket_connect_timeout: float = socket_connect_timeout
        self.socket_keepalive: bool = socket_keepalive
        self.socket_keepalive_options: Dict[str, Any] = socket_keepalive_options
        self.unix_socket_path: str = unix_socket_path
        self.encoding: str = encoding
        self.encoding_errors: str = encoding_errors
        self.decode_responses: bool = decode_responses
        self.retry_on_timeout: bool = retry_on_timeout
        self.ssl: bool = ssl
        self.ssl_keyfile: str = ssl_keyfile
        self.ssl_certfile: str = ssl_certfile
        self.ssl_cert_reqs: str = ssl_cert_reqs
        self.ssl_ca_certs: str = ssl_ca_certs
        self.ssl_check_hostname: bool = ssl_check_hostname
        self.max_connections: int = max_connections
        self.single_connection_client: bool = single_connection_client
        self.health_check_interval: int = health_check_interval
        self.client_name: str = client_name
        self.username: str = username

    @property
    def config(self) -> Dict:
        return self.__dict__

    def __hash__(self):
        check_sum = 0
        config = self.config
        for key in config:
            check_sum += key.__hash__()
            check_sum += getattr(config[key], '__hash__', lambda:0)()
        return check_sum


class ObFastApi(Config):

    def __init__(self, buc_key: str = "OBVOS_USER_SIGN", log_name: str = 'obfastapi', log_path: str = None, log_level: str = "INFO", log_interval: int = 1, log_count: int = 7):
        self.buc_key = buc_key
        self.log_name = log_name
        self.log_path = log_path
        self.log_level = log_level
        self.log_interval = log_interval
        self.log_count = log_count


class ConfigsUtil:

    MYSQL: Dict[str, MysqlConfig] = {}
    REDIS: Dict[str, RedisConfig] = {}
    OB_FAST_API = ObFastApi()

    @staticmethod
    def get_config(configs: Dict[str, Config], key:str) -> Config:
        config = configs.get(key)
        if not config:
            raise ConfigsError('Nu such config %s' % key)

        return config

    @staticmethod
    def set_config(configs: Dict[str, Config], key:str, config: Config):
        configs[key] = config

    @classmethod
    def get_mysql_config(cls, key: str) -> MysqlConfig:
        return cls.get_config(cls.MYSQL, key)

    @classmethod
    def set_mysql_config(cls, key: str, config: MysqlConfig):
        cls.set_config(cls.MYSQL, key, config)

    @classmethod
    def get_redis_config(cls, key: str) -> RedisConfig:
        return cls.get_config(cls.REDIS, key)

    @classmethod
    def set_redis_config(cls, key: str, config: RedisConfig):
        cls.set_config(cls.REDIS, key, config)

    @classmethod
    def get_obfastapi_config(cls, key: str):
        return getattr(cls.OB_FAST_API, key.lower(), '')

    @classmethod
    def set_obfastapi_config(cls, key: str, value: Any):
        setattr(cls.OB_FAST_API, key.lower(), value)