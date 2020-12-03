from contextlib import contextmanager
from typing import ContextManager, Iterator

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.string_source.source_from_lines import StringSourceFromLinesBase
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer


class StringSource(StringSourceFromLinesBase):
    def __init__(self,
                 contents: str,
                 tmp_file_space: DirFileSpace,
                 ):
        super().__init__()
        self._contents = contents
        self.__tmp_file_space = tmp_file_space

    @staticmethod
    def structure_builder_for(string: Renderer[str]) -> StringSourceStructureBuilder:
        return StringSourceStructureBuilder.of_details(
            syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
            (custom_details.StrRendererAsSingleLineWithMaxLenDetailsRenderer(string),)
        )

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self.structure_builder_for(rend_comb.ConstantR(self._contents))

    @property
    def may_depend_on_external_resources(self) -> bool:
        return False

    @property
    def as_str(self) -> str:
        return self._contents

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        yield iter([self._contents])

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space
