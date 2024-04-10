from copy import deepcopy
from typing import Dict

import asyncio
from aioredis.client import Redis
from .config import ConfigsUtil, RedisConfig


__all__ = ('RedisConnectionPoolFactory')


class RedisConnectionPoolFactory:

    _POOLS: Dict[RedisConfig, Redis] = {}

    @classmethod
    def get_instance(cls, key: str) -> Redis:
        config = ConfigsUtil.get_redis_config(key)
        config = deepcopy(config)
        if config not in cls._POOLS:
            cls._POOLS[config] = cls.create_instance(config)
        return cls._POOLS[config]

    @classmethod
    def create_instance(cls, config: RedisConfig) -> Redis:
        return Redis(**config.config)

