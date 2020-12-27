from contextlib import contextmanager
from typing import Callable, ContextManager, Iterator

from exactly_lib.impls.types.string_source.contents.contents_with_cached_path import \
    ContentsWithCachedPathFromAsLinesBase
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace

StringTransFun = Callable[[Iterator[str]], Iterator[str]]


class TransformedStringSourceFromLines(StringSource):
    def __init__(self,
                 transformation: StringTransFun,
                 transformed: StringSource,
                 transformation_may_depend_on_external_resources: bool,
                 get_transformer_structure: Callable[[], StructureRenderer],
                 ):
        self._transformed = transformed
        self._transformation = transformation
        self._transformation_may_depend_on_external_resources = transformation_may_depend_on_external_resources
        self._get_transformer_structure = get_transformer_structure

        self._contents = self._new_contents()

        self._is_frozen = False

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._transformed.new_structure_builder().with_transformed_by(self._get_transformer_structure())

    def freeze(self):
        if self._is_frozen:
            return

        self._transformed.freeze()
        self._contents = self._new_contents()
        self._is_frozen = True

    def contents(self) -> StringSourceContents:
        return self._contents

    def _new_contents(self) -> StringSourceContents:
        return _TransformedStringSourceContentsFromLines(
            self._transformation,
            self._transformed.contents(),
            self._transformation_may_depend_on_external_resources,
        )


class _TransformedStringSourceContentsFromLines(ContentsWithCachedPathFromAsLinesBase):
    def __init__(self,
                 transformation: StringTransFun,
                 transformed: StringSourceContents,
                 transformation_may_depend_on_external_resources: bool,
                 ):
        super().__init__()
        self._transformed = transformed
        self._transformation = transformation
        self._transformation_may_depend_on_external_resources = transformation_may_depend_on_external_resources

    @property
    def may_depend_on_external_resources(self) -> bool:
        return (self._transformation_may_depend_on_external_resources or
                self._transformed.may_depend_on_external_resources)

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._transformed.as_lines as lines:
            yield self._transformation(lines)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._transformed.tmp_file_space
