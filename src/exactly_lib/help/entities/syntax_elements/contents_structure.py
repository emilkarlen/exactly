from typing import Optional, List, Iterable, Sequence

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.definitions.entity.all_entity_types import SYNTAX_ELEMENT_ENTITY_TYPE_NAMES
from exactly_lib.definitions.entity.syntax_elements import SyntaxElementInfo
from exactly_lib.definitions.type_system import TypeCategory
from exactly_lib.help.contents_structure.entity import EntityTypeHelp, EntityDocumentation
from exactly_lib.impls.types.expression.grammar import Grammar
from exactly_lib.impls.types.expression.syntax_documentation import Syntax
from exactly_lib.util.textformat.structure import document, core
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents, SectionItem


class SyntaxElementDocumentation(EntityDocumentation):
    def __init__(self, syntax_element: SyntaxElementInfo):
        super().__init__(syntax_element)
        self._syntax_element = syntax_element

    @property
    def syntax_element(self) -> SyntaxElementInfo:
        return self._syntax_element

    @property
    def type_category(self) -> Optional[TypeCategory]:
        return self._syntax_element.type_category

    def main_description_rest(self) -> SectionContents:
        return SectionContents(self.main_description_rest_paragraphs(),
                               self.main_description_rest_sub_sections())

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        raise NotImplementedError('abstract method')

    def main_description_rest_sub_sections(self) -> List[SectionItem]:
        return []

    def notes(self) -> SectionContents:
        return SectionContents.empty()

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
                 type_category: Optional[TypeCategory],
                 name_and_cross_ref_target: SingularNameAndCrossReferenceId,
                 main_description_rest: Sequence[ParagraphItem],
                 main_description_rest_sub_sections: Sequence[SectionItem],
                 notes: SectionContents,
                 invokation_variants: List[InvokationVariant],
                 syntax_element_descriptions: List[SyntaxElementDescription],
                 see_also_targets: List[SeeAlsoTarget],
                 ):
        super().__init__(
            SyntaxElementInfo(
                name_and_cross_ref_target.singular_name,
                type_category,
                name_and_cross_ref_target.single_line_description_str,
                name_and_cross_ref_target.cross_reference_target,
            )
        )
        self._main_description_rest = main_description_rest
        self._main_description_rest_sub_sections = main_description_rest_sub_sections
        self._notes = notes
        self._invokation_variants = invokation_variants
        self._syntax_element_descriptions = syntax_element_descriptions
        self._see_also_targets = see_also_targets

    def main_description_rest_paragraphs(self) -> List[ParagraphItem]:
        return list(self._main_description_rest)

    def main_description_rest_sub_sections(self) -> List[SectionItem]:
        return list(self._main_description_rest_sub_sections)

    def notes(self) -> SectionContents:
        return self._notes

    def invokation_variants(self) -> List[InvokationVariant]:
        return self._invokation_variants

    def syntax_element_descriptions(self) -> List[SyntaxElementDescription]:
        return self._syntax_element_descriptions

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return self._see_also_targets


def syntax_element_documentation(type_category: Optional[TypeCategory],
                                 name_and_cross_ref_target: SingularNameAndCrossReferenceId,
                                 main_description_rest: Sequence[ParagraphItem],
                                 main_description_rest_sub_sections: Sequence[SectionItem],
                                 invokation_variants: List[InvokationVariant],
                                 syntax_element_descriptions: List[SyntaxElementDescription],
                                 see_also_targets: List[SeeAlsoTarget],
                                 notes: SectionContents = SectionContents.empty(),
                                 ) -> SyntaxElementDocumentation:
    return SyntaxElementDocumentationWithConstantValues(type_category,
                                                        name_and_cross_ref_target,
                                                        main_description_rest,
                                                        main_description_rest_sub_sections,
                                                        notes,
                                                        invokation_variants,
                                                        syntax_element_descriptions,
                                                        see_also_targets)


def syntax_elements_help(syntax_elements: Iterable[SyntaxElementDocumentation]) -> EntityTypeHelp:
    return EntityTypeHelp(SYNTAX_ELEMENT_ENTITY_TYPE_NAMES,
                          syntax_elements)


def for_type_with_grammar(type_info: SyntaxElementInfo,
                          grammar: Grammar) -> SyntaxElementDocumentation:
    syntax = Syntax(grammar)

    details_sections = []
    details_sections += _section_iff_has_paragraphs(_PRECEDENCES_HEADER, syntax.precedence_description())
    details_sections += _section_iff_has_paragraphs(_EVALUATION_HEADER, syntax.evaluation_description())
    details_sections += _section_iff_has_paragraphs(_SYNTAX_HEADER, syntax.syntax_description())
    description = grammar.description()

    return syntax_element_documentation(
        type_info.type_category,
        type_info,
        description.initial_paragraphs,
        description.sections,
        syntax.invokation_variants(),
        syntax.syntax_element_descriptions(),
        syntax.see_also_targets(),
        SectionContents([], details_sections),
    )


def _section_iff_has_paragraphs(header: str, paragraphs: Sequence[ParagraphItem]) -> Sequence[SectionItem]:
    return (
        (document.Section(core.StringText(header),
                          document.SectionContents(list(paragraphs))),)
        if paragraphs
        else
        ()
    )


_PRECEDENCES_HEADER = 'Operator precedence'
_EVALUATION_HEADER = 'Evaluation'
_SYNTAX_HEADER = 'Syntax'
