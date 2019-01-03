from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax

TRANSFORMER_OPTION_ALTERNATIVES = [
    '',
    argument_syntax.syntax_for_transformer_option(
        argument_syntax.syntax_for_replace_transformer('a', 'A')
    ),
]

TRANSFORMER_OPTION_ALTERNATIVES_ELEMENTS = [
    [],
    argument_syntax.arguments_for_transformer_option(
        argument_syntax.syntax_for_replace_transformer('a', 'A')
    ),
]
