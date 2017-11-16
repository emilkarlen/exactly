from exactly_lib.help_texts.name_and_cross_ref import EntityTypeNames
from exactly_lib.help_texts.names import formatting
from exactly_lib.util.name import name_with_plural_s, Name


def _command_line_names_as_singular_name(entity_type_identifier: str,
                                         name: Name) -> EntityTypeNames:
    return EntityTypeNames(entity_type_identifier,
                           name,
                           formatting.syntax_element(name.singular))


def _entity_arg_is_singular_name(entity_type_identifier: str,
                                 name: Name,
                                 ) -> EntityTypeNames:
    return EntityTypeNames(entity_type_identifier,
                           name,
                           formatting.syntax_element(name.singular))


SYMBOL_CONCEPT_NAME = name_with_plural_s('symbol')

CONCEPT_ENTITY_TYPE_NAMES = _command_line_names_as_singular_name('concept',
                                                                 name_with_plural_s('concept'))

ACTOR_ENTITY_TYPE_NAMES = _command_line_names_as_singular_name('actor',
                                                               name_with_plural_s('actor'))

CONF_PARAM_ENTITY_TYPE_NAMES = _entity_arg_is_singular_name('confparam',
                                                            name_with_plural_s('configuration parameter'))

SUITE_REPORTER_ENTITY_TYPE_NAMES = _entity_arg_is_singular_name('reporter',
                                                                name_with_plural_s('suite reporter'))

SYNTAX_ELEMENT_ENTITY_TYPE_NAMES = _entity_arg_is_singular_name('syntax',
                                                                name_with_plural_s('syntax element'))

TYPE_ENTITY_TYPE_NAMES = _command_line_names_as_singular_name('type',
                                                              name_with_plural_s('type'))

BUILTIN_SYMBOL_ENTITY_TYPE_NAMES = EntityTypeNames('builtin',
                                                   Name('builtin ' + SYMBOL_CONCEPT_NAME.singular,
                                                        'builtin ' + SYMBOL_CONCEPT_NAME.plural),
                                                   formatting.syntax_element(SYMBOL_CONCEPT_NAME.singular))

ALL_ENTITY_TYPES_IN_DISPLAY_ORDER = (
    CONCEPT_ENTITY_TYPE_NAMES,
    CONF_PARAM_ENTITY_TYPE_NAMES,
    TYPE_ENTITY_TYPE_NAMES,
    ACTOR_ENTITY_TYPE_NAMES,
    SYNTAX_ELEMENT_ENTITY_TYPE_NAMES,
    BUILTIN_SYMBOL_ENTITY_TYPE_NAMES,
    SUITE_REPORTER_ENTITY_TYPE_NAMES,
)
