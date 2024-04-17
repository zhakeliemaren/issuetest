from sqlalchemy import select, update, func
from sqlalchemy.exc import NoResultFound
from src.do.sync_config import SyncBranchMapping, SyncRepoMapping, LogDO
from .mysql_ao import MysqlAO
from src.utils.base import Singleton
from src.dto.sync_config import AllRepoDTO, GetBranchDTO, SyncRepoDTO, SyncBranchDTO, RepoDTO, BranchDTO
from typing import List
from src.do.sync_config import SyncDirect, SyncType


class BaseDAO(MysqlAO):
    def __init__(self, model_cls, *args, **kwargs):
        self.model_cls = model_cls
        super().__init__(*args, **kwargs)

    async def get(self, **kwargs):
        async with self._async_session() as session:
            async with session.begin():
                stmt = select(self.model_cls).filter_by(**kwargs)
                try:
                    result = await session.execute(stmt)
                    instance = result.scalar_one()
                    return instance
                except NoResultFound:
                    return None

    async def create(self, **kwargs):
        async with self._async_session() as session:
            async with session.begin():
                instance = self.model_cls(**kwargs)
                session.add(instance)
                await session.commit()
                return instance

    async def filter(self, **kwargs):
        async with self._async_session() as session:
            async with session.begin():
                query = select(self.model_cls)
                to_del_keys = []
                for key, value in kwargs.items():
                    if isinstance(key, str) and "__contains" in key:
                        query = query.filter(self.model_cls.__dict__[key[:-10]].like(f"%{value}%"))
                        to_del_keys.append(key)
                    elif isinstance(key, str) and key.endswith("__in"):
                        query = query.filter(self.model_cls.__dict__[key[:-4]].in_(value))
                        to_del_keys.append(key)
                for key in to_del_keys:
                    del kwargs[key]
                stmt = query.filter_by(**kwargs).order_by(self.model_cls.id.desc())
                result = await session.execute(stmt)
                return result.scalars().all()

    async def all(self):
        async with self._async_session() as session:
            async with session.begin():
                stmt = select(self.model_cls).order_by(self.model_cls.id.desc())
                result = await session.execute(stmt)
                instances = result.scalars().all()
                return instances

    async def delete(self, instance):
        async with self._async_session() as session:
            async with session.begin():
                await session.delete(instance)
                await session.commit()

    async def update(self, instance, **kwargs):
        async with self._async_session() as session:
            async with session.begin():
                merged_instance = await session.merge(instance)
                for attr, value in kwargs.items():
                    setattr(merged_instance, attr, value)
                await session.commit()
                await session.refresh(merged_instance)
                return merged_instance

    async def values_list(self, *fields):
        async with self._async_session() as session:
            async with session.begin():
                query = select(self.model_cls)

                if fields:
                    query = query.with_entities(*fields)

                result = await session.execute(query)
                rows = result.fetchall()

                if len(fields) == 1:
                    return [row[0] for row in rows]
                else:
                    return [tuple(row) for row in rows]


class SyncRepoDAO(BaseDAO, metaclass=Singleton):

    def __init__(self, *args, **kwargs):
        super().__init__(SyncRepoMapping, *args, **kwargs)

    async def create_repo(self, dto: SyncRepoDTO) -> RepoDTO:
        async with self._async_session() as session:
            async with session.begin():
                dto.sync_granularity = SyncType(dto.sync_granularity)
                dto.sync_direction = SyncDirect(dto.sync_direction)
                do = SyncRepoMapping(**dto.dict())
                session.add(do)
                await session.flush()
                data = RepoDTO(
                    enable=do.enable,
                    repo_name=do.repo_name,
                    internal_repo_address=do.internal_repo_address,
                    external_repo_address=do.external_repo_address,
                    sync_granularity=do.sync_granularity.name,
                    sync_direction=do.sync_direction.name
                )
                await session.commit()
                return data

    async def get_sync_repo(self, page_number: int, page_size: int, create_sort: bool) -> List[AllRepoDTO]:
        async with self._async_session() as session:
            async with session.begin():
                stmt = select(SyncRepoMapping)
                create_order = SyncRepoMapping.created_at if create_sort else SyncRepoMapping.created_at.desc()
                stmt = stmt.order_by(create_order).offset((page_number - 1) * page_size).limit(page_size)
                do_list: List[SyncRepoMapping] = (await session.execute(stmt)).scalars().all()
                datas = []
                for do in do_list:
                    data = AllRepoDTO(
                        id=do.id,
                        enable=do.enable,
                        repo_name=do.repo_name,
                        internal_repo_address=do.internal_repo_address,
                        external_repo_address=do.external_repo_address,
                        sync_granularity=do.sync_granularity.name,
                        sync_direction=do.sync_direction.name,
                        created_at=str(do.created_at)
                    )
                    datas.append(data)
                return datas


class SyncBranchDAO(BaseDAO, metaclass=Singleton):

    def __init__(self, *args, **kwargs):
        super().__init__(SyncBranchMapping, *args, **kwargs)

    async def create_branch(self, dto: SyncBranchDTO, repo_id: int) -> BranchDTO:
        async with self._async_session() as session:
            async with session.begin():
                do = SyncBranchMapping(**dto.dict(), repo_id=repo_id)
                session.add(do)
                await session.commit()
                data = BranchDTO(
                    id=do.id,
                    enable=do.enable,
                    internal_branch_name=do.internal_branch_name,
                    external_branch_name=do.external_branch_name
                )
                return data

    async def get_sync_branch(self, repo_id: int, page_number: int, page_size: int, create_sort: bool) -> List[GetBranchDTO]:
        async with self._async_session() as session:
            async with session.begin():
                stmt = select(SyncBranchMapping).where(SyncBranchMapping.repo_id == repo_id)
                create_order = SyncBranchMapping.created_at if create_sort else SyncBranchMapping.created_at.desc()
                stmt = stmt.order_by(create_order).offset((page_number - 1) * page_size).limit(page_size)
                do_list: List[SyncBranchMapping] = (await session.execute(stmt)).scalars().all()
                datas = []
                for do in do_list:
                    data = GetBranchDTO(
                        id=do.id,
                        enable=do.enable,
                        internal_branch_name=do.internal_branch_name,
                        external_branch_name=do.external_branch_name,
                        created_at=str(do.created_at)
                    )
                    datas.append(data)
                return datas

    async def sync_branch(self, repo_id: int) -> List[GetBranchDTO]:
        async with self._async_session() as session:
            async with session.begin():
                stmt = select(SyncBranchMapping).where(SyncBranchMapping.repo_id == repo_id,
                                                       SyncBranchMapping.enable == 1)
                do_list: List[SyncBranchMapping] = (await session.execute(stmt)).scalars().all()
                datas = []
                for do in do_list:
                    data = GetBranchDTO(
                        id=do.id,
                        enable=do.enable,
                        created_at=str(do.created_at),
                        internal_branch_name=do.internal_branch_name,
                        external_branch_name=do.external_branch_name
                    )
                    datas.append(data)
                return datas

    async def get_branch(self, repo_id: int, branch_name: str, dire: SyncDirect) -> List[GetBranchDTO]:
        async with self._async_session() as session:
            async with session.begin():
                if dire == SyncDirect.to_outer:
                    stmt = select(SyncBranchMapping).where(SyncBranchMapping.repo_id == repo_id,
                                                           SyncBranchMapping.enable.is_(True),
                                                           SyncBranchMapping.internal_branch_name == branch_name)
                else:
                    stmt = select(SyncBranchMapping).where(SyncBranchMapping.repo_id == repo_id,
                                                           SyncBranchMapping.enable.is_(True),
                                                           SyncBranchMapping.external_branch_name == branch_name)
                do_list: List[SyncBranchMapping] = (await session.execute(stmt)).scalars().all()
                datas = []
                for do in do_list:
                    data = GetBranchDTO(
                        id=do.id,
                        enable=do.enable,
                        created_at=str(do.created_at),
                        internal_branch_name=do.internal_branch_name,
                        external_branch_name=do.external_branch_name
                    )
                    datas.append(data)
                return datas


class LogDAO(BaseDAO, metaclass=Singleton):

    def __init__(self, *args, **kwargs):
        super().__init__(LogDO, *args, **kwargs)

    async def init_sync_repo_log(self, repo_name, direct, log_content):
        async with self._async_session() as session:
            async with session.begin():
                do = LogDO(repo_name=repo_name, sync_direct=direct, log=log_content)
                session.add(do)
            await session.commit()

    async def update_sync_repo_log(self, repo_name, direct, log_content):
        async with self._async_session() as session:
            async with session.begin():
                stmt = update(LogDO).where(LogDO.repo_name == repo_name,
                                           LogDO.branch_id.is_(None), LogDO.commit_id.is_(None)).\
                    values(
                    sync_direct=direct,
                    log=log_content,
                    # log_history=func.CONCAT(LogDO.log_history, log_content),
                    update_at=func.now()
                )
                await session.execute(stmt)
            await session.commit()

    async def init_branch_log(self, repo_name, direct, branch_id, commit_id, log_content):
        async with self._async_session() as session:
            async with session.begin():
                do = LogDO(repo_name=repo_name, sync_direct=direct, branch_id=branch_id,
                           commit_id=commit_id, log=log_content)
                session.add(do)
            await session.commit()

    async def update_branch_log(self, repo_name, direct, branch_id, commit_id, log_content):
        async with self._async_session() as session:
            async with session.begin():
                stmt = update(LogDO).where(LogDO.repo_name == repo_name, LogDO.branch_id == branch_id). \
                    values(
                    sync_direct=direct,
                    commit_id=commit_id,
                    log=log_content,
                    # log_history=func.CONCAT(LogDO.log_history, log_content),
                    update_at=func.now()
                )
                await session.execute(stmt)
            await session.commit()

