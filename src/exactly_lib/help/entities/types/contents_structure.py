from typing import List, Iterable, Sequence

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity.all_entity_types import TYPE_ENTITY_TYPE_NAMES
from exactly_lib.definitions.entity.syntax_elements import SyntaxElementInfo
from exactly_lib.definitions.entity.types import TypeNameAndCrossReferenceId
from exactly_lib.help.contents_structure.entity import EntityTypeHelp, EntityDocumentation
from exactly_lib.test_case_utils.expression import syntax_documentation
from exactly_lib.test_case_utils.expression.grammar import Grammar
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.str_.name import Name
from exactly_lib.util.textformat.structure.document import SectionContents


class TypeDocumentation(EntityDocumentation):
    def __init__(self,
                 type_category: TypeCategory,
                 name_and_cross_ref_target: TypeNameAndCrossReferenceId,
                 corresponding_syntax_element: SyntaxElementInfo,
                 main_description_rest: SectionContents,
                 custom_see_also_targets: Iterable[SeeAlsoTarget] = (),
                 syntax_elements: Sequence[SyntaxElementDescription] = ()):
        super().__init__(name_and_cross_ref_target)
        self._name_and_cross_ref_target = name_and_cross_ref_target
        self._type_identifier = name_and_cross_ref_target.identifier
        self._type_category = type_category
        self._corresponding_syntax_element = corresponding_syntax_element
        self._main_description_rest = main_description_rest
        self._custom_see_also_targets = list(custom_see_also_targets)
        self._syntax_elements = syntax_elements

    """
    Documents a type of the type system.
    """

    @property
    def type_category(self) -> TypeCategory:
        return self._type_category

    def type_identifier(self) -> str:
        return self._type_identifier

    def name(self) -> Name:
        return self._name_and_cross_ref_target.name

    def invokation_variants(self) -> List[InvokationVariant]:
        return []

    def main_description_rest(self) -> SectionContents:
        return self._main_description_rest

    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return self._syntax_elements

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return ([self._corresponding_syntax_element.cross_reference_target]
                +
                self._custom_see_also_targets
                )


class LogicTypeWithExpressionGrammarDocumentation(TypeDocumentation):
    def __init__(self,
                 name_and_cross_ref_target: TypeNameAndCrossReferenceId,
                 corresponding_syntax_element: SyntaxElementInfo,
                 grammar: Grammar,
                 main_description_rest: SectionContents):
        self._syntax = syntax_documentation.Syntax(grammar)
        main_description_rest = SectionContents(self._syntax.global_description() +
                                                main_description_rest.initial_paragraphs,
                                                main_description_rest.sections)
        super().__init__(TypeCategory.LOGIC,
                         name_and_cross_ref_target,
                         corresponding_syntax_element,
                         main_description_rest,
                         syntax_elements=self._syntax.syntax_element_descriptions())

    """
    Documents a type of the type system.
    """

    def invokation_variants(self) -> List[InvokationVariant]:
        return self._syntax.invokation_variants()

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return super().see_also_targets() + self._syntax.see_also_targets()


def types_help(types: Iterable[TypeDocumentation]) -> EntityTypeHelp:
    return EntityTypeHelp(TYPE_ENTITY_TYPE_NAMES,
                          types)
