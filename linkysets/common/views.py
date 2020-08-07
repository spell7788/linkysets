from __future__ import annotations

from typing import (
    ClassVar,
    Dict,
    Iterable,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from django.http import Http404, HttpRequest, HttpResponse


class QsObjectMeta(NamedTuple):
    name: str
    model: Union[str, Type[Model]]
    is_required: bool = True
    filter_field: str = "pk"


QsObjectTuple = Tuple[Optional[Model], QsObjectMeta]
FinalQsObjectTuple = Tuple[Model, QsObjectMeta]


class QuerystringObjectsMixin:
    request: HttpRequest

    qs_objects_meta: ClassVar[Sequence[QsObjectMeta]]
    qs_objects: Dict[str, FinalQsObjectTuple]

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        qs_objects = list(self._get_querystring_objects())
        for obj, meta in qs_objects:
            if obj is not None:
                continue

            try:
                return self.get_no_qs_object_response(meta)
            except NotImplementedError:
                name, model, *_ = meta
                model_string = model if isinstance(model, str) else model.__name__
                raise Http404(
                    f'Unable to get required "{model_string}" object '
                    f'from query string parameter "{name}".'
                )

        self.qs_objects = {
            meta.name: (obj, meta) for obj, meta in qs_objects  # type: ignore
        }
        return super().dispatch(request, *args, **kwargs)  # type: ignore

    def get_no_qs_object_response(self, meta: QsObjectMeta) -> HttpResponse:
        raise NotImplementedError(
            '"get_no_qs_object_response" should be implemented in a view class.'
        )

    def _get_querystring_objects(self) -> Iterable[QsObjectTuple]:
        querydict = self.request.GET
        for meta in self.qs_objects_meta:
            name, model_or_string, is_required, filter_field = meta

            if isinstance(model_or_string, str):
                model: Type[Model] = apps.get_model(model_or_string)
            else:
                model = model_or_string

            param_value = querydict.get(name)
            if not param_value and is_required:
                raise ValueError(
                    f'Querystring parameter "{name}" is required. Got value: {param_value}'
                )

            if not param_value and not is_required:
                continue

            try:
                obj = model._default_manager.get(**{filter_field: param_value})
            except ObjectDoesNotExist:
                yield None, meta
            else:
                yield obj, meta
