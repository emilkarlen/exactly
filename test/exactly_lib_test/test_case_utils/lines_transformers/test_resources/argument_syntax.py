from exactly_lib.help_texts import instruction_arguments
from exactly_lib.test_case_utils.lines_transformer import parse_lines_transformer
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib_test.test_case_utils.line_matcher.test_resources.argument_syntax import \
    syntax_for_arbitrary_line_matcher_without_symbol_references


def syntax_for_transformer_option(transformer_expression: str) -> str:
    return ' '.join([
        option_syntax(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
        transformer_expression,
    ])


def syntax_for_replace_transformer(regex_token_str: str,
                                   replacement_token_str: str) -> str:
    return ' '.join([
        parse_lines_transformer.REPLACE_TRANSFORMER_NAME,
        regex_token_str,
        replacement_token_str,
    ])


def syntax_for_select_transformer(line_matcher: str) -> str:
    return ' '.join([
        parse_lines_transformer.SELECT_TRANSFORMER_NAME,
        line_matcher,
    ])


def syntax_for_arbitrary_lines_transformer_without_symbol_references() -> str:
    return syntax_for_select_transformer(syntax_for_arbitrary_line_matcher_without_symbol_references())


def syntax_for_sequence_of_transformers(transformer_syntax_list: list) -> str:
    return (' ' + parse_lines_transformer.SEQUENCE_OPERATOR_NAME + ' ').join(transformer_syntax_list)
