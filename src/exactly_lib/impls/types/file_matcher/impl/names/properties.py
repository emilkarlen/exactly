from pathlib import Path
from typing import Callable

from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.types.matcher.property_getter import PropertyGetter
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcherModel
from exactly_lib.util.description_tree import renderers


class NamePartPropertyGetterBase(WithCachedNodeDescriptionBase):
    def __init__(self,
                 matcher_name: str,
                 get_name_part_from_name: Callable[[str], str]
                 ):
        super().__init__()
        self._matcher_name = matcher_name
        self._get_name_part_from_name = get_name_part_from_name

    def _structure(self) -> StructureRenderer:
        return renderers.header_only(self._matcher_name)


class NamePartAsStrPropertyGetter(PropertyGetter[FileMatcherModel, str],
                                  NamePartPropertyGetterBase):

    def get_from(self, model: FileMatcherModel) -> str:
        return self._get_name_part_from_name(model.path.primitive.name)


class NamePartAsPathPropertyGetter(PropertyGetter[FileMatcherModel, Path],
                                   NamePartPropertyGetterBase):
    def get_from(self, model: FileMatcherModel) -> Path:
        return Path(
            self._get_name_part_from_name(model.path.primitive.name)
        )


def get_name_from_name(name: str) -> str:
    return name


def get_stem_from_name(name: str) -> str:
    return name.split('.', maxsplit=1)[0]


def get_suffixes_from_name(name: str) -> str:
    dot_idx = name.find('.')
    return (
        ''
        if dot_idx == -1
        else
        name[dot_idx:]
    )


def get_suffix_from_name(name: str) -> str:
    dot_idx = name.rfind('.')
    return (
        ''
        if dot_idx == -1
        else
        name[dot_idx:]
    )


class NameAsStrPropertyGetter(PropertyGetter[FileMatcherModel, str],
                              WithCachedNodeDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(file_matcher.NAME_MATCHER_NAME)

    def get_from(self, model: FileMatcherModel) -> str:
        return model.path.primitive.name


class NameAsPathPropertyGetter(PropertyGetter[FileMatcherModel, Path],
                               WithCachedNodeDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(file_matcher.NAME_MATCHER_NAME)

    def get_from(self, model: FileMatcherModel) -> Path:
        return Path(model.path.primitive.name)


class WholePathAsStrPropertyGetter(PropertyGetter[FileMatcherModel, str],
                                   WithCachedNodeDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(file_matcher.WHOLE_PATH_MATCHER_NAME)

    def get_from(self, model: FileMatcherModel) -> str:
        return str(model.path.primitive)


class WholePathAsPathPropertyGetter(PropertyGetter[FileMatcherModel, Path],
                                    WithCachedNodeDescriptionBase):
    def _structure(self) -> StructureRenderer:
        return renderers.header_only(file_matcher.WHOLE_PATH_MATCHER_NAME)

    def get_from(self, model: FileMatcherModel) -> Path:
        return model.path.primitive
