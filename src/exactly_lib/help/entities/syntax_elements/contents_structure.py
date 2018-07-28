from typing import Optional, List, Iterable

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.entity.all_entity_types import SYNTAX_ELEMENT_ENTITY_TYPE_NAMES
from exactly_lib.help.contents_structure.entity import EntityTypeHelp, EntityDocumentation
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents, SectionItem


class SyntaxElementDocumentation(EntityDocumentation):
    def __init__(self,
                 type_category: Optional[TypeCategory],
                 name_and_cross_ref_target: SingularNameAndCrossReferenceId):
        super().__init__(name_and_cross_ref_target)
        self._type_category = type_category

    @property
    def type_category(self) -> Optional[TypeCategory]:
        return self._type_category

    def main_description_rest(self) -> SectionContents:
        return SectionContents(self.main_description_rest_paragraphs(),
                               self.main_description_rest_sub_sections())

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        raise NotImplementedError('abstract method')

    def main_description_rest_sub_sections(self) -> List[SectionItem]:
        return []

    def invokation_variants(self) -> List[InvokationVariant]:
        raise NotImplementedError('abstract method')

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        raise NotImplementedError('abstract method')

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        raise NotImplementedError('abstract method')


class SyntaxElementDocumentationWithConstantValues(SyntaxElementDocumentation):
    def __init__(self,
                 type_category: TypeCategory,
                 name_and_cross_ref_target: SingularNameAndCrossReferenceId,
                 main_description_rest: List[ParagraphItem],
                 invokation_variants: List[InvokationVariant],
                 syntax_element_descriptions: List[SyntaxElementDescription],
                 see_also_targets: List[SeeAlsoTarget]):
        super().__init__(type_category, name_and_cross_ref_target)
        self._main_description_rest = main_description_rest
        self._invokation_variants = invokation_variants
        self._syntax_element_descriptions = syntax_element_descriptions
        self._see_also_targets = see_also_targets

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return self._main_description_rest

    def invokation_variants(self) -> List[InvokationVariant]:
        return self._invokation_variants

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return self._syntax_element_descriptions

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return self._see_also_targets


def syntax_element_documentation(type_category: TypeCategory,
                                 name_and_cross_ref_target: SingularNameAndCrossReferenceId,
                                 main_description_rest: List[ParagraphItem],
                                 invokation_variants: List[InvokationVariant],
                                 syntax_element_descriptions: List[SyntaxElementDescription],
                                 see_also_targets: List[SeeAlsoTarget]) -> SyntaxElementDocumentation:
    return SyntaxElementDocumentationWithConstantValues(type_category,
                                                        name_and_cross_ref_target,
                                                        main_description_rest,
                                                        invokation_variants,
                                                        syntax_element_descriptions,
                                                        see_also_targets)


def syntax_elements_help(syntax_elements: Iterable[SyntaxElementDocumentation]) -> EntityTypeHelp:
    return EntityTypeHelp(SYNTAX_ELEMENT_ENTITY_TYPE_NAMES,
                          syntax_elements)
