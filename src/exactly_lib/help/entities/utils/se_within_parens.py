from typing import Optional, List

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args, \
    SyntaxElementDescription
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.symbol.value_type import TypeCategory
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionItem, SectionContents


class OptionallyWithinParens(SyntaxElementDocumentation):
    def __init__(self,
                 type_category: Optional[TypeCategory],
                 name_and_cross_ref_target: SingularNameAndCrossReferenceId,
                 primitive: SyntaxElementDocumentation,
                 ):
        super().__init__(type_category, name_and_cross_ref_target)
        self._primitive = primitive
        self._primitive_name = self.singular_name() + '\''

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return self._primitive.main_description_rest_paragraphs()

    def main_description_rest_sub_sections(self) -> List[SectionItem]:
        return self._primitive.main_description_rest_sub_sections()

    def notes(self) -> SectionContents:
        return self._primitive.notes()

    def invokation_variants(self) -> List[InvokationVariant]:
        primitive_arg = a.single_mandatory(a.Named(self._primitive_name))
        return [
            invokation_variant_from_args([primitive_arg]),
            invokation_variant_from_args([
                a.single_mandatory(a.Constant('(')),
                primitive_arg,
                a.single_mandatory(a.Constant(')')),
            ]),
        ]

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return [
            SyntaxElementDescription(
                self._primitive_name,
                (),
                self._primitive.invokation_variants(),
                (),
            )
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return self._primitive.see_also_targets()
