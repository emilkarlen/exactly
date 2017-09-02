from exactly_lib.help.utils.entity_documentation import EntitiesHelp, EntityDocumentationBase
from exactly_lib.help_texts.entity_names import TYPE_ENTITY_TYPE_NAME
from exactly_lib.help_texts.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId, Name


class TypeDocumentation(EntityDocumentationBase):
    def __init__(self,
                 type_identifier: str,
                 name_and_cross_ref_target: SingularAndPluralNameAndCrossReferenceId):
        super().__init__(name_and_cross_ref_target)
        self._name_and_cross_ref_target = name_and_cross_ref_target
        self._type_identifier = type_identifier

    """
    Documents a type of the type system.
    """

    def type_identifier(self) -> str:
        return self._type_identifier

    def name(self) -> Name:
        return self._name_and_cross_ref_target.name


def types_help(types: iter) -> EntitiesHelp:
    """
    :param types: [TypeDocumentation]
    """
    return EntitiesHelp(TYPE_ENTITY_TYPE_NAME, types)
