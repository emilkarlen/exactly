from exactly_lib.help.utils.entity_documentation import EntityTypeNames
from exactly_lib.help_texts.cross_reference_id import EntityCrossReferenceId
from exactly_lib.help_texts.entity.concepts import SYMBOL_CONCEPT_INFO
from exactly_lib.help_texts.entity_identifiers import BUILTIN_ENTITY_TYPE_IDENTIFIER
from exactly_lib.help_texts.name_and_cross_ref import SingularNameAndCrossReferenceId
from exactly_lib.help_texts.names import formatting
from exactly_lib.util.name import Name

BUILTIN_SYMBOL_ENTITY_TYPE_NAMES = EntityTypeNames(
    Name('builtin ' + SYMBOL_CONCEPT_INFO.singular_name,
         'builtin ' + SYMBOL_CONCEPT_INFO.plural_name),
    BUILTIN_ENTITY_TYPE_IDENTIFIER,
    formatting.syntax_element(SYMBOL_CONCEPT_INFO.singular_name))


def type_cross_ref(symbol_name: str) -> EntityCrossReferenceId:
    return EntityCrossReferenceId(BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.identifier,
                                  BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.name.singular,
                                  symbol_name)


def name_and_ref_target(symbol_name: str,
                        single_line_description_str: str) -> SingularNameAndCrossReferenceId:
    return SingularNameAndCrossReferenceId(symbol_name,
                                           single_line_description_str,
                                           type_cross_ref(symbol_name))
