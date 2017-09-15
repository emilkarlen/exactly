from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.check_with_neg_and_rel_opts import \
    InstructionArgumentsVariantConstructor
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig
from exactly_lib_test.test_case_utils.parse.test_resources.selection_arguments import file_matcher_arguments
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration


class AssertionVariantArgumentsConstructor:
    """"
    Constructs a string for the arguments that are specific for one of the assertion variants:
    - empty
    - num-files

    Argument string is constructed by __str__
    """

    def __str__(self):
        raise NotImplementedError('abstract method')


class CommonArgumentsConstructor(InstructionArgumentsVariantConstructor):
    """
    Constructs a string for the common arguments used by all assertion variants:
    - [RELATIVITY]
    - PATH
    - [SELECTION]
    - [NEGATION]
    """

    def __init__(self,
                 path: str,
                 file_matcher: str = ''):
        self._path = path
        self._file_matcher = file_matcher

    def apply(self,
              etc: ExpectationTypeConfig,
              rel_opt_config: RelativityOptionConfiguration) -> str:
        return '{relativity} {path} {selection} {negation}'.format(
            relativity=rel_opt_config.option_string,
            path=self._path,
            selection=self._empty_if_no_file_matcher_otherwise_selection(),
            negation=etc.nothing__if_positive__not_option__if_negative)

    def _empty_if_no_file_matcher_otherwise_selection(self) -> str:
        if self._file_matcher:
            return option_syntax(instruction_arguments.SELECTION_OPTION.name) + ' ' + self._file_matcher
        else:
            return ''


class CompleteArgumentsConstructor(InstructionArgumentsVariantConstructor):
    """
    Constructs a string for "complete" instruction arguments - common arguments
    followed by arguments for an assertion variant.
    """

    def __init__(self,
                 common_arguments: CommonArgumentsConstructor,
                 assertion_variant: AssertionVariantArgumentsConstructor,
                 ):
        self._common_arguments = common_arguments
        self._assertion_variant = assertion_variant

    def apply(self,
              etc: ExpectationTypeConfig,
              rel_opt_config: RelativityOptionConfiguration) -> str:
        return '{common} {assertion_variant}'.format(
            common=self._common_arguments.apply(etc, rel_opt_config),
            assertion_variant=str(self._assertion_variant))


class EmptyAssertionVariant(AssertionVariantArgumentsConstructor):
    def __str__(self):
        return EMPTINESS_CHECK_ARGUMENT


class NumFilesAssertionVariant(AssertionVariantArgumentsConstructor):
    def __init__(self,
                 condition: str):
        self._condition = condition

    def __str__(self):
        return '{num_files} {condition}'.format(
            num_files=sut.NUM_FILES_CHECK_ARGUMENT,
            condition=self._condition)


def replace_not_op(etc: ExpectationTypeConfig, s: str) -> str:
    return s.replace('<not_opt>', etc.nothing__if_positive__not_option__if_negative)


def arguments_constructor_for_variant(path: str,
                                      variant: AssertionVariantArgumentsConstructor) -> CompleteArgumentsConstructor:
    return CompleteArgumentsConstructor(
        CommonArgumentsConstructor(path),
        variant)


def instruction_arguments_for_emptiness_check(rel_opt: RelativityOptionConfiguration,
                                              file_name: str) -> str:
    complete_args = arguments_constructor_for_variant(file_name,
                                                      EmptyAssertionVariant())
    return complete_args.apply(ExpectationTypeConfig(ExpectationType.POSITIVE),
                               rel_opt)


def arguments_with_selection_options(file_name: str,
                                     assertion_variant: AssertionVariantArgumentsConstructor,
                                     name_option_pattern: str = '',
                                     type_matcher: FileType = None,
                                     named_matcher: str = '',
                                     ) -> CompleteArgumentsConstructor:
    file_matcher = file_matcher_arguments(name_option_pattern,
                                          type_matcher,
                                          named_matcher)

    return CompleteArgumentsConstructor(
        CommonArgumentsConstructor(file_name,
                                   file_matcher=file_matcher),
        assertion_variant)
