from typing import List

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements


def syntax_for_transformer_option(transformer_expression: str) -> str:
    return ' '.join([
        option_syntax(string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
        transformer_expression,
    ])


def arguments_for_transformer_option(transformer_expression: str) -> List[str]:
    return [
        option_syntax(string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
        transformer_expression,
    ]


def syntax_for_replace_transformer(regex_token_str: str,
                                   replacement_token_str: str) -> str:
    return ' '.join([
        names.REPLACE_TRANSFORMER_NAME,
        regex_token_str,
        replacement_token_str,
    ])


def syntax_for_replace_transformer__custom(arguments: Arguments) -> Arguments:
    return Arguments(names.REPLACE_TRANSFORMER_NAME).followed_by(arguments)


def syntax_for_run(program: ArgumentElements, ignore_exit_code: bool = False) -> Arguments:
    st_arguments = [string_transformer.RUN_PROGRAM]
    if ignore_exit_code:
        st_arguments.append(
            option_syntax(string_transformer.WITH_IGNORED_EXIT_CODE_OPTION_NAME)
        )
    argument_elements = ArgumentElements(st_arguments).append_to_first_and_following_lines(program)
    return argument_elements.as_arguments


def syntax_for_filter_transformer(line_matcher: str) -> str:
    return ' '.join([
        names.FILTER_TRANSFORMER_NAME,
        line_matcher,
    ])


def syntax_for_sequence_of_transformers(transformer_syntax_list: list) -> str:
    return (' ' + names.SEQUENCE_OPERATOR_NAME + ' ').join(
        transformer_syntax_list)


def arbitrary_value_on_single_line() -> str:
    return syntax_for_replace_transformer('REGEX', 'REPLACEMENT')


def to_lower_case() -> str:
    return names.TO_LOWER_CASE


def to_upper_case() -> str:
    return names.TO_UPPER_CASE
