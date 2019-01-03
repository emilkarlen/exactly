from typing import List

from exactly_lib.definitions import instruction_arguments
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.util.cli_syntax.option_syntax import option_syntax


def syntax_for_transformer_option(transformer_expression: str) -> str:
    return ' '.join([
        option_syntax(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
        transformer_expression,
    ])


def arguments_for_transformer_option(transformer_expression: str) -> List[str]:
    return [
        option_syntax(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
        transformer_expression,
    ]


def syntax_for_replace_transformer(regex_token_str: str,
                                   replacement_token_str: str) -> str:
    return ' '.join([
        parse_string_transformer.REPLACE_TRANSFORMER_NAME,
        regex_token_str,
        replacement_token_str,
    ])


def syntax_for_select_transformer(line_matcher: str) -> str:
    return ' '.join([
        parse_string_transformer.SELECT_TRANSFORMER_NAME,
        line_matcher,
    ])


def syntax_for_sequence_of_transformers(transformer_syntax_list: list) -> str:
    return (' ' + parse_string_transformer.SEQUENCE_OPERATOR_NAME + ' ').join(transformer_syntax_list)


def arbitrary_value_on_single_line() -> str:
    return syntax_for_replace_transformer('REGEX', 'REPLACEMENT')
