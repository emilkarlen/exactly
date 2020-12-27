from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.description_tree import custom_details
from exactly_lib.impls.types.string_source.contents.contents_of_str import ContentsOfStr
from exactly_lib.impls.types.string_source.source_from_contents import StringSourceWConstantContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer


class FactoryOfStringSourceStructureBuilder:
    def __init__(self, string: Renderer[str]):
        self._string = string

    def new(self) -> StringSourceStructureBuilder:
        return StringSourceStructureBuilder.of_details(
            syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
            (custom_details.StrRendererAsSingleLineWithMaxLenDetailsRenderer(
                self._string
            ),
            )
        )


def string_source(contents: str,
                  tmp_file_space: DirFileSpace,
                  ) -> StringSource:
    return StringSourceWConstantContents(
        FactoryOfStringSourceStructureBuilder(rend_comb.ConstantR(contents)).new,
        ContentsOfStr(contents, None, tmp_file_space),
    )
