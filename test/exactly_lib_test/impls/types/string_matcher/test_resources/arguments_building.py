from exactly_lib.definitions import logic
from exactly_lib.definitions import path as path_texts
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib.impls.types.string_source import defs as str_src_defs
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.logic_types import Quantifier, ExpectationType
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import \
    nothing__if_positive__not_option__if_negative
from exactly_lib_test.section_document.test_resources.parse_source import ParseSourceBuilder


class FileContentsArgumentsConstructor:
    """"
    Constructs a string for the arguments that are specific for one of the assertion variants:
    - empty
    - num-lines
    - ...

    Argument string is constructed by __str__
    """

    def __str__(self):
        raise NotImplementedError('abstract method')


class CommonArgumentsConstructor:
    """
    Constructs a string for the common arguments used by all assertion variants:
    - [TRANSFORMATION]
    - [NEGATION]
    """

    def __init__(self, file_transformer: str = ''):
        self._file_transformer = file_transformer

    def apply(self, expectation_type: ExpectationType) -> str:
        return '{transformation} {negation}'.format(
            transformation=self._empty_if_no_file_transformer_otherwise_selection(),
            negation=nothing__if_positive__not_option__if_negative(expectation_type))

    def _empty_if_no_file_transformer_otherwise_selection(self) -> str:
        if self._file_transformer:
            return ' '.join([option_syntax(string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
                             self._file_transformer,
                             ])
        else:
            return ''


class ImplicitActualFileArgumentsConstructor:
    """
    Constructs a string for arguments of a contents instruction - common arguments
    followed by arguments for an assertion variant.
    """

    def __init__(self,
                 common_arguments: CommonArgumentsConstructor,
                 assertion_variant: FileContentsArgumentsConstructor,
                 ):
        self._common_arguments = common_arguments
        self._assertion_variant = assertion_variant

    def apply(self, expectation_type: ExpectationType) -> str:
        return '{common} {assertion_variant}'.format(
            common=self._common_arguments.apply(expectation_type),
            assertion_variant=str(self._assertion_variant))


class EmptyAssertionArgumentsConstructor(FileContentsArgumentsConstructor):
    def __str__(self):
        return matcher_options.EMPTY_ARGUMENT


class NumLinesAssertionArgumentsConstructor(FileContentsArgumentsConstructor):
    def __init__(self, condition: str):
        self._condition = condition

    def __str__(self):
        return matcher_options.NUM_LINES_ARGUMENT + ' ' + self._condition


class EqualsStringAssertionArgumentsConstructor(FileContentsArgumentsConstructor):
    def __init__(self, string_argument: str):
        """
        :param string_argument: Must be a single token.
        """
        self._string_argument = string_argument

    def __str__(self):
        return matcher_options.EQUALS_ARGUMENT + ' ' + self._string_argument


class LineMatchesAssertionArgumentsConstructor(FileContentsArgumentsConstructor):
    def __init__(self,
                 quantifier: Quantifier,
                 line_matcher: str):
        self.quantifier = quantifier
        self._condition = line_matcher

    def __str__(self):
        return '{any_or_every} {line} {quantifier_separator} {condition}'.format(
            any_or_every=logic.QUANTIFIER_ARGUMENTS[self.quantifier],
            line=matcher_options.LINE_ARGUMENT,
            quantifier_separator=logic.QUANTIFICATION_SEPARATOR_ARGUMENT,
            condition=self._condition,
        )


def args(arg_str: str, **kwargs) -> str:
    if kwargs:
        format_map = dict(list(_FORMAT_MAP.items()) + list(kwargs.items()))
        return arg_str.format_map(format_map)
    return arg_str.format_map(_FORMAT_MAP)


FULL_MATCH_ARGUMENT = option_syntax(matcher_options.FULL_MATCH_ARGUMENT_OPTION)

_FORMAT_MAP = {
    'any': logic.EXISTS_QUANTIFIER_ARGUMENT,
    'every': logic.ALL_QUANTIFIER_ARGUMENT,
    'empty': matcher_options.EMPTY_ARGUMENT,
    'equals': matcher_options.EQUALS_ARGUMENT,
    'matches': matcher_options.MATCHES_ARGUMENT,
    'file_option': option_syntax(str_src_defs.FILE_OPTION),
    'full_match': FULL_MATCH_ARGUMENT,
    'not': matcher_options.NOT_ARGUMENT,
    'transform_option': option_syntax(string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
    'rel_hds_case_option': path_texts.REL_HDS_CASE_OPTION,
    'rel_cwd_option': path_texts.REL_CWD_OPTION,
    'rel_tmp_option': path_texts.REL_TMP_OPTION,
    'rel_symbol_option': path_texts.REL_symbol_OPTION,
}

SB = ParseSourceBuilder(_FORMAT_MAP)


def arbitrary_single_line_value_that_must_not_be_quoted() -> str:
    return matcher_options.EMPTY_ARGUMENT
