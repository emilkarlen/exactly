from exactly_lib_test.test_case_utils.lines_transformers.test_resources import argument_syntax

TRANSFORMER_OPTION_ALTERNATIVES = [
    '',
    argument_syntax.syntax_for_transformer_option(
        argument_syntax.syntax_for_replace_transformer('a', 'A')
    ),
]
