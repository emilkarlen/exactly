from exactly_lib.test_case_utils.lines_transformers import parse_lines_transformer
from exactly_lib.util.cli_syntax.option_syntax import option_syntax


def syntax_for_transformer_option(transformer_expression: str) -> str:
    return ' '.join([
        option_syntax(parse_lines_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
        transformer_expression,
    ])


def syntax_for_replace_transformer(regex_token_str: str,
                                   replacement_token_str: str) -> str:
    return ' '.join([
        parse_lines_transformer.REPLACE_TRANSFORMER_NAME,
        regex_token_str,
        replacement_token_str,
    ])


def syntax_for_sequence_of_transformers(transformer_syntax_list: list) -> str:
    return (' ' + parse_lines_transformer.SEQUENCE_OPERATOR_NAME + ' ').join(transformer_syntax_list)
