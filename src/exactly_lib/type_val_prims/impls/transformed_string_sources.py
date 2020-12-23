from abc import ABC
from contextlib import contextmanager
from typing import Callable, ContextManager, Iterator

from exactly_lib.impls.types.string_source.source_from_lines import StringSourceFromLinesBase
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace

StringTransFun = Callable[[Iterator[str]], Iterator[str]]


class TransformedStringSourceBase(StringSource, ABC):
    def __init__(self,
                 transformed: StringSource,
                 ):
        super().__init__()
        self._transformed = transformed

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self._transformed._tmp_file_space


class TransformedStringSourceFromLinesWFreezeOfTransformedBase(StringSourceFromLinesBase, TransformedStringSourceBase,
                                                               ABC):
    def __init__(self,
                 transformation: StringTransFun,
                 transformed: StringSource,
                 transformation_may_depend_on_external_resources: bool,
                 ):
        StringSourceFromLinesBase.__init__(self)
        TransformedStringSourceBase.__init__(self, transformed)
        self._transformation = transformation
        self._transformation_may_depend_on_external_resources = transformation_may_depend_on_external_resources

    @property
    def may_depend_on_external_resources(self) -> bool:
        return (self._transformation_may_depend_on_external_resources or
                self._transformed.may_depend_on_external_resources)

    def freeze(self):
        self._transformed.freeze()

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._transformed.as_lines as lines:
            yield self._transformation(lines)


class TransformedStringSourceFromLines(TransformedStringSourceFromLinesWFreezeOfTransformedBase):
    def __init__(self,
                 transformation: StringTransFun,
                 transformed: StringSource,
                 transformation_may_depend_on_external_resources: bool,
                 get_transformer_structure: Callable[[], StructureRenderer],
                 ):
        TransformedStringSourceFromLinesWFreezeOfTransformedBase.__init__(self,
                                                                          transformation,
                                                                          transformed,
                                                                          transformation_may_depend_on_external_resources)
        self._get_transformer_structure = get_transformer_structure

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._transformed.new_structure_builder().with_transformed_by(self._get_transformer_structure())
