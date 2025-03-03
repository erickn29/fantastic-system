from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError
from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (
    InstrumentedAttribute,
    aliased,
    joinedload,
    relationship,
    selectinload,
)

from core.database import DatabaseHelper
from model.base import Base
from tools.sentry import sentry_message


T = TypeVar("T", bound=Base)


class F:
    def __init__(
        self,
        or_conditions: list | None = None,
        **expressions,
    ):
        self._expressions = expressions
        self.or_conditions: list[dict[str, Any]] = or_conditions or []
        if not self.or_conditions:
            self.or_conditions.append({"or": {**self._expressions}})

    def __iter__(self):
        return iter(self.or_conditions)

    def __or__(self, other):
        new_f_or_conditions = self.or_conditions + other.or_conditions
        new_f = F(or_conditions=new_f_or_conditions, **self._expressions)
        return new_f


class FilterCondition:
    EXACT = "exact"
    NOT_EXACT = "not_exact"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NOT_IN = "not_in"
    LIKE = "like"
    ILIKE = "ilike"
    BETWEEN = "between"
    ANY = "any"

    @classmethod
    def get_by_expr(cls, expr: str = EXACT):
        conditions_map = {
            cls.EXACT: lambda column, value: column == value,
            cls.NOT_EXACT: lambda column, value: column != value,
            cls.GT: lambda column, value: column > value,
            cls.GTE: lambda column, value: column >= value,
            cls.LT: lambda column, value: column < value,
            cls.LTE: lambda column, value: column <= value,
            cls.IN: lambda column, value: column.in_(value),
            cls.NOT_IN: lambda column, value: column.not_in(value),
            cls.LIKE: lambda column, value: column.like(f"%{value}%"),
            cls.ILIKE: lambda column, value: column.ilike(f"%{value}%"),
            cls.BETWEEN: lambda column, value: column.between(*value),
            cls.ANY: lambda column, value: column.any(value),
        }
        if expr not in FilterCondition.__dict__.values():
            raise ValueError(f"Неподдерживаемый фильтр {expr}")
        return conditions_map.get(expr)

    @classmethod
    def get_filter(cls, value: Any, expr: str = EXACT):
        return {expr: value}


class BaseRepository:
    model: type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _get_filters(filters: dict, model: type[T], *args, **kwargs):
        filter_conditions = []
        for key, value in filters.items():
            column = getattr(model, key) if isinstance(key, str) else key
            if not isinstance(value, dict):
                value = {FilterCondition.EXACT: value}
            for operator, operand in value.items():
                condition = FilterCondition.get_by_expr(operator)
                if condition:
                    filter_conditions.append(condition(column, operand))
        return (
            and_(*filter_conditions)
            if len(filter_conditions) > 1
            else filter_conditions[0]
        )

    @staticmethod
    def _get_simple_filters(filters: dict) -> dict:
        simple_filters = {}
        for k, v in filters.items():
            if k.startswith("join__"):
                continue
            key = k
            value = v
            if "__" in k:
                key = k.split("__")[0]
                value = {k.split("__")[1]: v}
            simple_filters[key] = value
        return simple_filters

    def _get_join_filters(
        self, filters: dict, statement: Select
    ) -> tuple[dict, Select]:
        filters_for_join = {}
        joins = {}
        for k, v in filters.items():
            if k.startswith("join__") and "__" in k:
                k = k.lstrip("join__")  # noqa: B005
                filters_for_join[k] = v

        join_filters = {}
        for k, v in filters_for_join.items():
            relation_name, attr_name = k.split("__", 1)
            relation = getattr(self.model, relation_name)

            if relation_name not in joins:
                alias = aliased(relation.property.mapper.class_)
                joins[relation_name] = alias
                statement = statement.join(alias)

            value = v
            if "__" in k.split("__", 1)[1]:
                expr = k.split("__")[2]
                value = {expr: v}
            join_filters[getattr(joins[relation_name], attr_name.split("__")[0])] = (
                value
            )
        return join_filters, statement

    def _get_conditions(self, filters: dict, statement: Select):
        conditions = []
        if simple_filters := self._get_simple_filters(filters):
            conditions.append(self._get_filters(simple_filters, self.model))
        join_filters, statement = self._get_join_filters(filters, statement)
        if join_filters:
            conditions.append(self._get_filters(join_filters, self.model))
        return conditions, statement

    def get_statement(
        self,
        expressions: F | None = None,
        excludes: dict[InstrumentedAttribute, Any] | None = None,
        joined_load: list[relationship] | None = None,  # type: ignore
        select_in_load: list[relationship] | None = None,  # type: ignore
        order_by: list[InstrumentedAttribute] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        count: bool = False,
        **filters,
    ) -> Select:
        statement = (
            select(self.model)
            if not count
            else select(func.count(1)).select_from(self.model)
        )
        conditions = []
        if expressions:
            for expr in expressions:
                for _k, v in expr.items():
                    condition, statement = self._get_conditions(v, statement)
                    conditions.append([condition])
        if filters:
            condition, statement = self._get_conditions(filters, statement)
            conditions.append([condition])
        statement = statement.filter(or_(*[and_(*c[0]) for c in conditions]))
        if excludes:
            for field, value in excludes.items():
                statement = statement.where(field != value)
        if joined_load:
            statement = statement.options(*[joinedload(item) for item in joined_load])
        if select_in_load:
            statement = statement.options(
                *[selectinload(item) for item in select_in_load]
            )
        if offset is not None:
            statement = statement.offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        if not count:
            order_by = order_by if order_by is not None else self.model.ordering()
            statement = statement.order_by(*order_by)
        return statement

    async def all(
        self,
        joined_load: list[relationship] | None = None,  # type: ignore
        select_in_load: list[relationship] | None = None,  # type: ignore
        order_by: list[InstrumentedAttribute] | None = None,
    ) -> Sequence[T]:
        statement = self.get_statement(
            joined_load=joined_load,
            select_in_load=select_in_load,
            order_by=order_by,
        )
        result = await self.session.scalars(statement=statement)
        return result.all()

    async def count(
        self,
        excludes: dict[InstrumentedAttribute, Any] | None = None,
        **filters,
    ) -> int:
        statement = self.get_statement(
            count=True,
            excludes=excludes,
            **filters,
        )
        result = await self.session.scalar(statement=statement)
        return result

    async def exists(
        self,
        excludes: dict[InstrumentedAttribute, Any] | None = None,
        **filters,
    ) -> bool:
        subquery = self.get_statement(excludes=excludes, **filters)
        statement = select(1).where(subquery.exists())
        result = await self.session.scalar(statement=statement)
        return bool(result)

    async def filter(
        self,
        expressions: F | None = None,
        excludes: dict[InstrumentedAttribute, Any] | None = None,
        joined_load: list[relationship] | None = None,  # type: ignore
        select_in_load: list[relationship] | None = None,  # type: ignore
        order_by: list[InstrumentedAttribute] | None = None,
        limit: int | None = None,
        offset: int | None = None,
        **filters,
    ) -> Sequence[T]:
        statement = self.get_statement(
            expressions=expressions,
            excludes=excludes,
            joined_load=joined_load,
            select_in_load=select_in_load,
            order_by=order_by,
            limit=limit,
            offset=offset,
            **filters,
        )
        result = await self.session.scalars(statement=statement)
        return result.all()

    async def get(
        self,
        expressions: F | None = None,
        excludes: dict[InstrumentedAttribute, Any] | None = None,
        joined_load: list[relationship] | None = None,  # type: ignore
        select_in_load: list[relationship] | None = None,  # type: ignore
        **filters,
    ) -> T:
        statement = self.get_statement(
            expressions=expressions,
            excludes=excludes,
            joined_load=joined_load,
            select_in_load=select_in_load,
            **filters,
        )
        result = await self.session.execute(statement=statement)
        return result.scalar_one()

    async def get_or_none(self, **filters):
        statement = self.get_statement(**filters)
        result = await self.session.execute(statement=statement)
        return result.scalar_one_or_none()

    async def find(
        self,
        expressions: F | None = None,
        excludes: dict[InstrumentedAttribute, Any] | None = None,
        joined_load: list[relationship] | None = None,  # type: ignore
        select_in_load: list[relationship] | None = None,  # type: ignore
        order_by: list[InstrumentedAttribute] | None = None,
        **filters,
    ) -> T | None:
        statement = self.get_statement(
            expressions=expressions,
            excludes=excludes,
            joined_load=joined_load,
            select_in_load=select_in_load,
            order_by=order_by,
            **filters,
        )
        result = await self.session.scalar(statement=statement)
        return result

    async def create(self, commit: bool = True, **model_data) -> T:
        instance = self.model(**model_data)
        self.session.add(instance)
        await self.session.commit() if commit else await self.session.flush()
        return instance  # type: ignore

    async def update(self, instance: T, commit: bool = True, **model_data) -> T:
        for key, value in model_data.items():
            setattr(instance, key, value)
        self.session.add(instance)
        await self.session.commit() if commit else await self.session.flush()
        return instance

    async def delete(self, instance: T, commit: bool = True) -> None:
        await self.session.delete(instance)
        await self.session.commit() if commit else await self.session.flush()

    async def get_or_create(
        self, filters: list[str], commit: bool = True, **model_data
    ):
        created = True
        get_filters = {
            filter: model_data.get(filter) for filter in filters
        } or model_data
        if instance := await self.find(**get_filters):
            created = False
            return instance, created
        return await self.create(commit, **model_data), created

    async def update_or_create(
        self, filters: dict[str, Any], commit: bool = True, **model_data
    ):
        created = True
        if instance := await self.get_or_none(**filters):
            created = False
            return (
                await self.update(instance=instance, commit=commit, **model_data),
                created,
            )
        model_data.update(filters)
        return await self.create(commit, **model_data), created


class SARepository:
    def __init__(self, connection: DatabaseHelper):
        self._session = None
        self._conn = connection

    def stmt(self, model: type[T]):
        class StmtWrapper:
            def __init__(self, session_: AsyncSession, model_: type[T]):
                self._session = session_
                self._model = model_
                self._base_repo = BaseRepository(self._session)
                self._base_repo.model = self._model

            def _to_dto(self, model_object: T, dto: BaseModel) -> BaseModel | None:
                try:
                    result = dto.model_validate(model_object)
                except ValidationError as err:
                    error_text = (
                        f"Ошибка преобразования объекта <{self._model.__name__}>.\n"
                        f"Данные для преобразования {model_object}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:to_dto",
                    )
                    raise err
                return result

            async def create(
                self, dto: BaseModel = None, **model_data
            ) -> T | BaseModel | None:
                """
                Создает новую запись модели и сохраняет ее в базе данных.

                Args:
                    dto: Объект для преобразования результата в объект DTO.
                    **model_data: Атрибуты и значения нового экземпляра модели.

                Returns:
                    T: Созданная и сохраненная запись модели.
                """
                try:
                    result = await self._base_repo.create(commit=False, **model_data)
                    if dto:
                        return self._to_dto(result, dto)
                    return result
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка создания объекта <{self._model.__name__}>.\n"
                        f"Данные для создания {model_data}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:create",
                    )
                    raise SQLAlchemyError(error_text) from err

            async def delete(self, instance: T) -> None:
                """
                Удаляет существующую запись модели из базы данных.

                Args:
                    instance: Экземпляр модели для удаления.
                """
                try:
                    await self._base_repo.delete(instance, commit=False)
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка удаления объекта <{self._model.__name__}>.\n"
                        f"Данные для удаления {instance}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:delete",
                    )
                    raise SQLAlchemyError(error_text) from err

            async def get_or_create(
                self, filters: list[str], dto: BaseModel | None = None, **model_data
            ) -> tuple[T | BaseModel, bool]:
                """
                Ищет существующую запись модели по заданным фильтрам или создаёт
                новую запись,
                если не найдена.

                Args:
                    dto: Объект для преобразования результата в объект DTO.
                    filters: Список ключевых слов для поиска экземпляра модели.
                    **model_data: Атрибуты и значения нового экземпляра модели.

                Returns:
                    tuple[T, bool]: Кортеж: созданный или найденный экземпляр
                    модели и флаг, указывающий, была ли запись
                    создана (True) или найдена (False).
                """
                try:
                    result, created = await self._base_repo.get_or_create(
                        filters,
                        commit=False,
                        **model_data,
                    )
                    if dto:
                        return self._to_dto(result, dto), created
                    return result, created
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка получения объекта <{self._model.__name__}>.\n"
                        f"Данные для фильтрации {filters}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:repo_get_or_create",
                    )
                    raise SQLAlchemyError(error_text) from err

            async def update(
                self, instance: T, dto: BaseModel | None = None, **model_data
            ) -> T | BaseModel:
                """
                Обновляет существующую запись модели и сохраняет
                изменения в базе данных.

                Args:
                    dto: Объект для преобразования результата в объект DTO.
                    instance: Экземпляр модели для обновления.
                    **model_data: Атрибуты и значения для обновления экземпляра модели.

                Returns:
                    T: Обновленный экземпляр модели.
                """
                try:
                    result = await self._base_repo.update(
                        instance=instance,
                        commit=False,
                        **model_data,
                    )
                    if dto:
                        return self._to_dto(result, dto)
                    return result
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка получения объекта <{self._model.__name__}>.\n"
                        f"Данные для обновления {instance}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:repo_update",
                    )
                    raise SQLAlchemyError(error_text) from err

            async def update_or_create(
                self,
                filters: dict[str, Any],
                dto: BaseModel | None = None,
                **model_data,
            ) -> tuple[T | BaseModel, bool]:
                """
                Обновляет существующую запись модели по заданным фильтрам или
                создаёт новую
                запись, если не найдена.

                Parameters:
                    dto: Объект для преобразования результата в объект DTO.
                    filters (dict[str, Any]): Словарь ключевых слов и
                    значений для поиска
                    экземпляра модели.
                    **model_data: Атрибуты и значения нового экземпляра модели.

                Returns:
                    tuple[T, bool]: Пару значения: обновленный или созданный
                    экземпляр
                    модели и флаг, указывающий, была ли запись
                    создана (True) или найдена (False)
                """
                try:
                    result, created = await self._base_repo.update_or_create(
                        filters,
                        commit=False,
                        **model_data,
                    )
                    if dto:
                        return self._to_dto(result, dto), created
                    return result, created
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка получения объекта <{self._model.__name__}>.\n"
                        f"Данные для фильтрации {filters}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:repo_update_or_create",
                    )
                    raise SQLAlchemyError(error_text) from err

        if not self._session:
            raise AttributeError("Вызов возможен только внутри контекстного менеджера")
        return StmtWrapper(self._session, model)

    def query(self, model: type[T]):
        class QueryWrapper:
            def __init__(
                self, session_: AsyncSession, model_: type[T], is_session_exists: bool
            ):
                self._session = session_
                self._model = model_
                self._base_repo = BaseRepository(self._session)
                self._base_repo.model = self._model
                self._session_exists = is_session_exists

            def _to_dto(self, model_object: T, dto: BaseModel) -> BaseModel | None:
                if not model_object or not dto:
                    return None
                try:
                    result = dto.model_validate(model_object)
                except ValidationError as err:
                    error_text = (
                        f"Ошибка преобразования объекта <{self._model.__name__}>.\n"
                        f"Данные для преобразования {model_object}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:to_dto",
                    )
                    return None
                return result

            async def all(
                self,
                joined_load: list[relationship] | None = None,  # type: ignore
                select_in_load: list[relationship] | None = None,  # type: ignore
                order_by: list[InstrumentedAttribute] | None = None,
                dto: BaseModel = None,
            ) -> Sequence[T] | list[BaseModel]:
                """
                Возвращает список объектов модели или список DTO.

                Args:
                    joined_load: Список отношений для использования joinedload.
                    (many-to-one, one-to-one)
                    select_in_load: Список отношений для использования selectinload.
                    (one-to-many, many-to-many)
                    order_by: Список атрибутов для сортировки результата.
                    dto: Объект для преобразования результата в объект DTO.

                Returns:
                    Sequence[T]: Список объектов модели.
                """
                try:
                    result = await self._base_repo.all(
                        joined_load=joined_load,
                        select_in_load=select_in_load,
                        order_by=order_by,
                    )
                    if dto:
                        return [self._to_dto(obj, dto) for obj in result]
                    return result
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка получения объекта <{self._model.__name__}>.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:repo_all",
                    )
                    raise SQLAlchemyError(error_text) from err
                finally:
                    if not self._session_exists:
                        await self._session.close()

            async def count(
                self,
                excludes: dict[InstrumentedAttribute, Any] | None = None,
                **filters,
            ) -> int:
                """
                Возвращает количество объектов модели,
                удовлетворяющих заданным фильтрам.

                Args:
                    excludes: Словарь атрибутов и значений для исключения из результата.
                    **filters: Именованные аргументы для добавления в фильтр запроса.

                Returns:
                    int: Количество записей модели.
                """
                try:
                    result = await self._base_repo.count(
                        excludes,
                        **filters,
                    )
                    return result
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка получения объекта <{self._model.__name__}>.\n"
                        f"Данные для фильтрации {filters}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:repo_count",
                    )
                    raise SQLAlchemyError(error_text) from err
                finally:
                    if not self._session_exists:
                        await self._session.close()

            async def get(
                self,
                expressions: F | None = None,
                excludes: dict[InstrumentedAttribute, Any] | None = None,
                joined_load: list[relationship] | None = None,  # type: ignore
                select_in_load: list[relationship] | None = None,  # type: ignore
                dto: BaseModel = None,
                **filters,
            ) -> T | BaseModel:
                """
                Возвращает единственную запись модели, удовлетворяющую заданным фильтрам
                или DTO.

                Args:
                    expressions: F условия OR для фильтрации записей.
                    excludes: Словарь атрибутов и значений для исключения из результата.
                    joined_load: Список отношений для использования joinedload.
                    (many-to-one, one-to-one)
                    select_in_load: Список отношений для использования selectinload.
                    (one-to-many, many-to-many)
                    dto: Объект для преобразования результата в объект DTO.
                    **filters: Именованные аргументы для добавления в фильтр запроса.

                Returns:
                    T: Единственная запись модели,
                    удовлетворяющая заданным фильтрам.

                Raises:
                    NoResultFound: Если не найдена единственная запись
                    MultipleResultsFound: Если найдено более одной записи.
                """
                try:
                    result = await self._base_repo.get(
                        expressions=expressions,
                        excludes=excludes,
                        joined_load=joined_load,
                        select_in_load=select_in_load,
                        **filters,
                    )
                    if dto:
                        return self._to_dto(result, dto)
                    return result
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка получения объекта <{self._model.__name__}>.\n"
                        f"Данные для фильтрации {filters}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:repo_get",
                    )
                    raise SQLAlchemyError(error_text) from err
                finally:
                    if not self._session_exists:
                        await self._session.close()

            async def exists(
                self,
                excludes: dict[InstrumentedAttribute, Any] | None = None,
                **filters,
            ) -> bool:
                """
                Проверяет наличие записей модели, удовлетворяющих заданным фильтрам.

                Args:
                    excludes: Словарь атрибутов и значений для исключения из результата.
                    **filters: Именованные аргументы для добавления в фильтр запроса.

                Returns:
                    bool: True, если есть записи модели, иначе False.
                """
                try:
                    result = await self._base_repo.exists(
                        excludes,
                        **filters,
                    )
                    return result
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка получения объекта <{self._model.__name__}>.\n"
                        f"Данные для фильтрации {filters}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:repo_exists",
                    )
                    raise SQLAlchemyError(error_text) from err
                finally:
                    if not self._session_exists:
                        await self._session.close()

            async def filter(
                self,
                expressions: F | None = None,
                dto: BaseModel = None,
                excludes: dict[InstrumentedAttribute, Any] | None = None,
                joined_load: list[relationship] | None = None,  # type: ignore
                select_in_load: list[relationship] | None = None,  # type: ignore
                order_by: list[InstrumentedAttribute] | None = None,
                limit: int | None = None,
                offset: int | None = None,
                **filters,
            ) -> Sequence[T] | list[BaseModel]:
                """
                Возвращает список записей модели, удовлетворяющих заданным фильтрам.

                Args:
                    expressions: F условия OR для фильтрации записей.
                    excludes: Словарь атрибутов и значений для исключения из результата.
                    joined_load: Список отношений для использования joinedload.
                    (many-to-one, one-to-one)
                    select_in_load: Список отношений для использования selectinload.
                    (one-to-many, many-to-many)
                    order_by: Список атрибутов для сортировки результата.
                    limit: Максимальное количество результатов.
                    offset: Порядковый номер начального результата (сдвиг).
                    dto: Объект для преобразования результата в объект DTO.
                    **filters: Именованные аргументы для добавления в фильтр запроса.

                Returns:
                    Sequence[T]: Список записей модели.
                """
                try:
                    result = await self._base_repo.filter(
                        expressions=expressions,
                        excludes=excludes,
                        joined_load=joined_load,
                        select_in_load=select_in_load,
                        order_by=order_by,
                        limit=limit,
                        offset=offset,
                        **filters,
                    )
                    if dto:
                        return [self._to_dto(obj, dto) for obj in result]
                    return result
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка получения объекта <{self._model.__name__}>.\n"
                        f"Данные для фильтрации {filters}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:repo_filter",
                    )
                    raise SQLAlchemyError(error_text) from err
                finally:
                    if not self._session_exists:
                        await self._session.close()

            async def find(
                self,
                expressions: F | None = None,
                dto: BaseModel | None = None,
                excludes: dict[InstrumentedAttribute, Any] | None = None,
                joined_load: list[relationship] | None = None,  # type: ignore
                select_in_load: list[relationship] | None = None,  # type: ignore
                order_by: list[InstrumentedAttribute] | None = None,
                **filters,
            ) -> T | BaseModel | None:
                """
                Возвращает первую запись модели, удовлетворяющую заданным фильтрам,
                или None, если не найдено ни одной.

                Args:
                    expressions: F условия OR для фильтрации записей.
                    dto: Объект для преобразования результата в объект DTO.
                    excludes: Словарь атрибутов и значений для исключения из результата.
                    joined_load: Список отношений для использования joinedload.
                    (many-to-one, one-to-one)
                    select_in_load: Список отношений для использования selectinload.
                    (one-to-many, many-to-many)
                    order_by: Список атрибутов для сортировки результата.
                    **filters: Именованные аргументы для добавления в фильтр запроса.

                Returns:
                    T | None: Первая запись модели, удовлетворяющая заданным
                    фильтрам,
                    или None, если не найдено ни одной.
                """
                try:
                    result = await self._base_repo.find(
                        expressions=expressions,
                        excludes=excludes,
                        joined_load=joined_load,
                        select_in_load=select_in_load,
                        order_by=order_by,
                        **filters,
                    )
                    if dto:
                        return self._to_dto(result, dto)
                    return result
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка получения объекта <{self._model.__name__}>.\n"
                        f"Данные для фильтрации {filters}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:repo_find",
                    )
                    raise SQLAlchemyError(error_text) from err
                finally:
                    if not self._session_exists:
                        await self._session.close()

            async def get_or_none(self, dto: BaseModel | None = None, **filters):
                """
                Ищет единственную запись модели по заданным фильтрам и возвращает ее,
                если она
                существует, или None, если не найдена.

                Args:
                    dto: Объект для преобразования результата в объект DTO.
                    **filters: Набор ключевых слов для поиска экземпляра модели.

                Returns:
                    T | None: Первая запись модели, удовлетворяющая фильтрам,
                    или None если не найдено ни одной.

                Raises:
                    MultipleResultsFound: Если найдено более одной записи.
                """
                try:
                    result = await self._base_repo.get_or_none(
                        **filters,
                    )
                    if dto:
                        return self._to_dto(result, dto)
                    return result
                except SQLAlchemyError as err:
                    error_text = (
                        f"Ошибка получения объекта <{self._model.__name__}>.\n"
                        f"Данные для фильтрации {filters}.\n"
                        f"Текст ошибки в исключении {str(err)}.\n"
                    )
                    sentry_message(
                        message=error_text,
                        level="error",
                        title="CHATTER:repo_get_or_none",
                    )
                    raise SQLAlchemyError(error_text) from err
                finally:
                    if not self._session_exists:
                        await self._session.close()

        session_exists = self._session is not None
        session = self._conn.session_factory() if not session_exists else self._session
        return QueryWrapper(session, model, session_exists)

    def _check_session(self):
        if not self._session:
            raise ValueError("Вызов возможен только внутри контекстного менеджера")

    async def __aenter__(self):
        self._session: AsyncSession = self._conn.session_factory()
        await self._session.begin()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._session.rollback()
            await self._session.close()
            self._session = None
            return
        await self._session.commit()
        await self._session.close()
        self._session = None
