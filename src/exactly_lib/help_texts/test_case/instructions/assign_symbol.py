from exactly_lib.help_texts.argument_rendering import cl_syntax, path_syntax
from exactly_lib.util.cli_syntax.elements import argument as a

PATH_TYPE = 'path'
STRING_TYPE = 'string'
EQUALS_ARGUMENT = '='

SYMBOL_NAME = 'NAME'
STRING_VALUE = 'STRING'

PATH_SUFFIX_IS_REQUIRED = False


def definition_of_type_string() -> str:
    string_type = a.Single(a.Multiplicity.MANDATORY, a.Constant(STRING_TYPE))
    string_value = a.Single(a.Multiplicity.MANDATORY, a.Named(STRING_VALUE))
    arguments_for_string_type = [
        string_type,
        _symbol_name(),
        _equals(),
        string_value,
    ]
    return cl_syntax.cl_syntax_for_args(arguments_for_string_type)


def definition_of_type_path() -> str:
    path_type = a.Single(a.Multiplicity.MANDATORY, a.Constant(PATH_TYPE))
    arguments_for_path_type = [
        path_type,
        _symbol_name(),
        _equals(),
    ]
    arguments_for_path_type.extend(
        path_syntax.mandatory_path_with_optional_relativity(
            path_syntax.PATH_ARGUMENT,
            True,
            PATH_SUFFIX_IS_REQUIRED))
    return cl_syntax.cl_syntax_for_args(arguments_for_path_type)


def _symbol_name() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.MANDATORY, a.Named(SYMBOL_NAME))


def _equals() -> a.ArgumentUsage:
    return a.Single(a.Multiplicity.MANDATORY, a.Constant(EQUALS_ARGUMENT))
