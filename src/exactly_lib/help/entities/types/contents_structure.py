from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase, \
    command_line_names_as_singular_name
from exactly_lib.help_texts.entity.concepts import TYPE_CONCEPT_INFO
from exactly_lib.help_texts.entity.types import TypeNameAndCrossReferenceId
from exactly_lib.test_case_utils.expression import syntax_documentation
from exactly_lib.test_case_utils.expression.grammar import Grammar
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.name import Name

TYPE_ENTITY_TYPE_NAMES = command_line_names_as_singular_name(TYPE_CONCEPT_INFO.name)


class TypeDocumentation(EntityDocumentationBase):
    def __init__(self,
                 type_category: TypeCategory,
                 name_and_cross_ref_target: TypeNameAndCrossReferenceId):
        super().__init__(name_and_cross_ref_target)
        self._name_and_cross_ref_target = name_and_cross_ref_target
        self._type_identifier = name_and_cross_ref_target.identifier
        self._type_category = type_category

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

    def invokation_variants(self) -> list:
        """
        :rtype [`InvokationVariant`]:
        """
        return []

    def see_also_targets(self) -> list:
        """
        :returns: A new list of :class:`SeeAlsoTarget`, which may contain duplicate elements.
        """
        return []


class LogicTypeWithExpressionGrammarDocumentation(TypeDocumentation):
    def __init__(self,
                 name_and_cross_ref_target: TypeNameAndCrossReferenceId,
                 grammar: Grammar):
        super().__init__(TypeCategory.LOGIC,
                         name_and_cross_ref_target)
        self._syntax = syntax_documentation.Syntax(grammar)

    """
    Documents a type of the type system.
    """

    def invokation_variants(self) -> list:
        return self._syntax.invokation_variants()

    def see_also_targets(self) -> list:
        return self._syntax.see_also_targets()


def types_help(types: iter) -> EntitiesHelp:
    """
    :param types: [TypeDocumentation]
    """
    return EntitiesHelp(TYPE_ENTITY_TYPE_NAMES,
                        types)
