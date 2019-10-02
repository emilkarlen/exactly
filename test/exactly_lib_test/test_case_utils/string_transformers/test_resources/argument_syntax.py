from typing import List

import exactly_lib.test_case_utils.string_transformer.names
from exactly_lib.definitions import instruction_arguments
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
        exactly_lib.test_case_utils.string_transformer.names.REPLACE_TRANSFORMER_NAME,
        regex_token_str,
        replacement_token_str,
    ])


def syntax_for_select_transformer(line_matcher: str) -> str:
    return ' '.join([
        exactly_lib.test_case_utils.string_transformer.names.SELECT_TRANSFORMER_NAME,
        line_matcher,
    ])


def syntax_for_sequence_of_transformers(transformer_syntax_list: list) -> str:
    return (' ' + exactly_lib.test_case_utils.string_transformer.names.SEQUENCE_OPERATOR_NAME + ' ').join(
        transformer_syntax_list)


def arbitrary_value_on_single_line() -> str:
    return syntax_for_replace_transformer('REGEX', 'REPLACEMENT')
