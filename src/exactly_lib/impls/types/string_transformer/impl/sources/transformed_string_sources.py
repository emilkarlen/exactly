from abc import ABC, abstractmethod
from typing import Iterator, Callable, Optional, TextIO

from exactly_lib.impls.types.string_source import cached_frozen
from exactly_lib.impls.types.string_source.contents import contents_via_write_to
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.impls import transformed_string_sources
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


def transformed_string_source_from_writer(write: Callable[[StringSourceContents, TextIO], None],
                                          model: StringSource,
                                          get_transformer_structure: Callable[[], StructureRenderer],
                                          mem_buff_size: int,
                                          file_name: Optional[str] = None,
                                          ) -> StringSource:
    def new_structure_builder() -> StringSourceStructureBuilder:
        return model.new_structure_builder().with_transformed_by(get_transformer_structure())

    model_contents = model.contents()
    return cached_frozen.StringSourceWithCachedFrozen(
        new_structure_builder,
        contents_via_write_to.ContentsViaWriteTo(
            model_contents.tmp_file_space,
            _WriterOfTransformed(write, model_contents),
            file_name,
        ),
        mem_buff_size,
        file_name,
    )


class _WriterOfTransformed(contents_via_write_to.Writer):
    def __init__(self,
                 write_transformed: Callable[[StringSourceContents, TextIO], None],
                 source: StringSourceContents,
                 ):
        self._write_transformed = write_transformed
        self._source = source

    def write(self, tmp_file_space: DirFileSpace, output: TextIO):
        self._write_transformed(self._source, output)
