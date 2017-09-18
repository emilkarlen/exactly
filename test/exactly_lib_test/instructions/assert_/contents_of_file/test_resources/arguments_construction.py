from exactly_lib.help_texts import instruction_arguments, file_ref as file_ref_texts
from exactly_lib.help_texts.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.logic_types import Quantifier
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig


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

    def __init__(self,
                 file_transformer: str = ''):
        self._file_transformer = file_transformer

    def apply(self, etc: ExpectationTypeConfig) -> str:
        return '{transformation} {negation}'.format(
            transformation=self._empty_if_no_file_transformer_otherwise_selection(),
            negation=etc.nothing__if_positive__not_option__if_negative)

    def _empty_if_no_file_transformer_otherwise_selection(self) -> str:
        if self._file_transformer:
            return option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME) + ' ' + self._file_transformer
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

    def apply(self, etc: ExpectationTypeConfig) -> str:
        return '{common} {assertion_variant}'.format(
            common=self._common_arguments.apply(etc),
            assertion_variant=str(self._assertion_variant))


class EmptyAssertionArgumentsConstructor(FileContentsArgumentsConstructor):
    def __str__(self):
        return instruction_options.EMPTY_ARGUMENT


class NumLinesAssertionArgumentsConstructor(FileContentsArgumentsConstructor):
    def __init__(self, condition: str):
        self._condition = condition

    def __str__(self):
        return instruction_options.NUM_LINES_ARGUMENT + ' ' + self._condition


class EqualsStringAssertionArgumentsConstructor(FileContentsArgumentsConstructor):
    def __init__(self, string_argument: str):
        """
        :param string_argument: Must be a single token.
        """
        self._string_argument = string_argument

    def __str__(self):
        return instruction_options.EQUALS_ARGUMENT + ' ' + self._string_argument


class LineMatchesAssertionArgumentsConstructor(FileContentsArgumentsConstructor):
    def __init__(self,
                 quantifier: Quantifier,
                 line_matcher: str):
        self.quantifier = quantifier
        self._condition = line_matcher

    def __str__(self):
        return '{any_or_every} {line_matches} {condition}'.format(
            any_or_every=instruction_arguments.QUANTIFIER_ARGUMENTS[self.quantifier],
            line_matches=instruction_options.LINE_ARGUMENT + ' ' + instruction_options.MATCHES_ARGUMENT,
            condition=self._condition,
        )


def args(arg_str: str, **kwargs) -> str:
    if kwargs:
        format_map = dict(list(_FORMAT_MAP.items()) + list(kwargs.items()))
        return arg_str.format_map(format_map)
    return arg_str.format_map(_FORMAT_MAP)


_FORMAT_MAP = {
    'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
    'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
    'line_matches': instruction_options.LINE_ARGUMENT + ' ' + instruction_options.MATCHES_ARGUMENT,
    'empty': instruction_options.EMPTY_ARGUMENT,
    'equals': instruction_options.EQUALS_ARGUMENT,
    'file_option': option_syntax(parse_here_doc_or_file_ref.FILE_ARGUMENT_OPTION),
    'not': instruction_options.NOT_ARGUMENT,
    'transform_option': option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
    'rel_home_case_option': file_ref_texts.REL_HOME_CASE_OPTION,
    'rel_cwd_option': file_ref_texts.REL_CWD_OPTION,
    'rel_tmp_option': file_ref_texts.REL_TMP_OPTION,
    'rel_symbol_option': file_ref_texts.REL_symbol_OPTION,
}
