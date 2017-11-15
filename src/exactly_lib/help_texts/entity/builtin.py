from exactly_lib.help_texts import entity_identifiers
from exactly_lib.help_texts.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId


def type_cross_ref(symbol_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(entity_identifiers.BUILTIN_ENTITY_TYPE_IDENTIFIER, symbol_name)


def name_and_ref_target(symbol_name: str,
                        single_line_description_str: str) -> SingularNameAndCrossReferenceId:
    return SingularNameAndCrossReferenceId(symbol_name,
                                           single_line_description_str,
                                           type_cross_ref(symbol_name))
