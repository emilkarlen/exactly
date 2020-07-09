from exactly_lib.definitions.cross_ref.name_and_cross_ref import EntityTypeNames
from exactly_lib.util.str_.name import a_name_with_plural_s, NameWithGender, an_name_with_plural_s


def _command_line_names_as_singular_name(entity_type_identifier: str,
                                         name: NameWithGender) -> EntityTypeNames:
    return EntityTypeNames(entity_type_identifier,
                           name)


def _entity_arg_is_singular_name(entity_type_identifier: str,
                                 name: NameWithGender,
                                 ) -> EntityTypeNames:
    return EntityTypeNames(entity_type_identifier,
                           name)


SYMBOL_CONCEPT_NAME = a_name_with_plural_s('symbol')

CONCEPT_ENTITY_TYPE_NAMES = _command_line_names_as_singular_name('concept',
                                                                 a_name_with_plural_s('concept'))

ACTOR_ENTITY_TYPE_NAMES = _command_line_names_as_singular_name('actor',
                                                               an_name_with_plural_s('actor'))

CONF_PARAM_ENTITY_TYPE_NAMES = _entity_arg_is_singular_name('confparam',
                                                            a_name_with_plural_s('configuration parameter'))

SUITE_REPORTER_ENTITY_TYPE_NAMES = _entity_arg_is_singular_name('reporter',
                                                                a_name_with_plural_s('suite reporter'))

DIRECTIVE_ENTITY_TYPE_NAMES = EntityTypeNames('directive',
                                              a_name_with_plural_s('directive'))

SYNTAX_ELEMENT_ENTITY_TYPE_NAMES = _entity_arg_is_singular_name('syntax',
                                                                a_name_with_plural_s('syntax element'))

TYPE_ENTITY_TYPE_NAMES = _command_line_names_as_singular_name('type',
                                                              a_name_with_plural_s('type'))

BUILTIN_SYMBOL_ENTITY_TYPE_NAMES = EntityTypeNames('builtin',
                                                   NameWithGender('a',
                                                                  'builtin ' + SYMBOL_CONCEPT_NAME.singular,
                                                                  'builtin ' + SYMBOL_CONCEPT_NAME.plural))

ALL_ENTITY_TYPES_IN_DISPLAY_ORDER = (
    CONCEPT_ENTITY_TYPE_NAMES,
    CONF_PARAM_ENTITY_TYPE_NAMES,
    TYPE_ENTITY_TYPE_NAMES,
    ACTOR_ENTITY_TYPE_NAMES,
    SYNTAX_ELEMENT_ENTITY_TYPE_NAMES,
    DIRECTIVE_ENTITY_TYPE_NAMES,
    BUILTIN_SYMBOL_ENTITY_TYPE_NAMES,
    SUITE_REPORTER_ENTITY_TYPE_NAMES,
)
