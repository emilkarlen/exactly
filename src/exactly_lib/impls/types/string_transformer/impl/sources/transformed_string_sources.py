from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Callable, ContextManager, IO, Optional

from exactly_lib.impls.types.string_source import cached_frozen
from exactly_lib.impls.types.string_source.contents_handler import handler_via_write_to
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.impls import transformed_string_sources
from exactly_lib.type_val_prims.impls.transformed_string_sources import TransformedStringSourceBase
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace


class StringTransformerFromLinesTransformer(StringTransformer, ABC):
    @abstractmethod
    def _transform(self, lines: Iterator[str]) -> Iterator[str]:
        pass

    @abstractmethod
    def _transformation_may_depend_on_external_resources(self) -> bool:
        pass

    def transform(self, model: StringSource) -> StringSource:
        return transformed_string_sources.TransformedStringSourceFromLines(
            self._transform,
            model,
            self._transformation_may_depend_on_external_resources(),
            self.structure,
        )


def transformed_string_source_from_writer(write: Callable[[StringSource, IO], None],
                                          transformed: StringSource,
                                          get_transformer_structure: Callable[[], StructureRenderer],
                                          mem_buff_size: int,
                                          file_name: Optional[str] = None,
                                          ) -> StringSource:
    def new_structure_builder() -> StringSourceStructureBuilder:
        return transformed.new_structure_builder().with_transformed_by(get_transformer_structure())

    return cached_frozen.StringSourceWithCachedFrozen(
        new_structure_builder,
        handler_via_write_to.ContentsHandlerViaWriteTo(
            transformed._tmp_file_space,
            _WriterOfTransformed(write, transformed),
            file_name,
        ),
        mem_buff_size,
        file_name,
    )


class _WriterOfTransformed(handler_via_write_to.Writer):
    def __init__(self,
                 write_transformed: Callable[[StringSource, IO], None],
                 source: StringSource,
                 ):
        self._write_transformed = write_transformed
        self._source = source

    def write(self, tmp_file_space: DirFileSpace, output: IO):
        self._write_transformed(self._source, output)


class _TransformedStringSourceFromWriter(TransformedStringSourceBase):
    def __init__(self,
                 write: Callable[[StringSource, IO], None],
                 transformed: StringSource,
                 get_transformer_structure: Callable[[], StructureRenderer],
                 ):
        super().__init__(transformed)
        self._write = write
        self._file_created_on_demand = None
        self._get_transformer_structure = get_transformer_structure

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._transformed.new_structure_builder().with_transformed_by(self._get_transformer_structure())

    def freeze(self):
        pass

    @property
    def may_depend_on_external_resources(self) -> bool:
        return True

    @property
    def as_file(self) -> Path:
        if self._file_created_on_demand is None:
            self._file_created_on_demand = self._mk_file()

        return self._file_created_on_demand

    @property
    def as_str(self) -> str:
        with self.as_file.open() as f:
            return f.read()

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self.as_file.open() as lines:
            yield lines

    def write_to(self, output: IO):
        if self._file_created_on_demand is None:
            self._write(self._transformed, output)
        else:
            with self._file_created_on_demand.open() as f:
                output.writelines(f.readlines())

    def _mk_file(self) -> Path:
        ret_val = self._tmp_file_space.new_path('transformed')
        with ret_val.open('x') as f:
            self.write_to(f)

        return ret_val
