from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase
from exactly_lib.help_texts.entity_names import TYPE_ENTITY_TYPE_NAME
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId, Name
from exactly_lib.test_case_utils.expression import syntax_documentation
from exactly_lib.test_case_utils.expression.grammar import Grammar
from exactly_lib.type_system.value_type import ElementType


class TypeDocumentation(EntityDocumentationBase):
    def __init__(self,
                 element_type: ElementType,
                 type_identifier: str,
                 name_and_cross_ref_target: SingularAndPluralNameAndCrossReferenceId):
        super().__init__(name_and_cross_ref_target)
        self._name_and_cross_ref_target = name_and_cross_ref_target
        self._type_identifier = type_identifier
        self._element_type = element_type

    """
    Documents a type of the type system.
    """

    @property
    def element_type(self) -> ElementType:
        return self._element_type

    def type_identifier(self) -> str:
        return self._type_identifier

    def name(self) -> Name:
        return self._name_and_cross_ref_target.name

    def invokation_variants(self) -> list:
        """
        :rtype [`InvokationVariant`]:
        """
        return []


class LogicTypeWithExpressionGrammarDocumentation(TypeDocumentation):
    def __init__(self,
                 type_identifier: str,
                 name_and_cross_ref_target: SingularAndPluralNameAndCrossReferenceId,
                 grammar: Grammar):
        super().__init__(ElementType.LOGIC, type_identifier, name_and_cross_ref_target)
        self._syntax = syntax_documentation.Syntax(grammar)

    """
    Documents a type of the type system.
    """

    def invokation_variants(self) -> list:
        return self._syntax.invokation_variants()


def types_help(types: iter) -> EntitiesHelp:
    """
    :param types: [TypeDocumentation]
    """
    return EntitiesHelp(TYPE_ENTITY_TYPE_NAME, types)
