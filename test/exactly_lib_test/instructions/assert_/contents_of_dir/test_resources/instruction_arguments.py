from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.assert_ import contents_of_dir as sut
from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.check_with_neg_and_rel_opts import \
    InstructionArgumentsVariantConstructor, InstructionArgumentsVariantConstructorWithTemplateStringBase
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig
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
            return option_syntax(instruction_arguments.SELECTION_OPTION) + ' ' + self._file_matcher
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
                 comparator: str,
                 right_operand: str):
        self._comparator = comparator
        self._right_operand = right_operand

    def __str__(self):
        return '{num_files} {operator} {right_operand}'.format(
            num_files=sut.NUM_FILES_CHECK_ARGUMENT,
            operator=self._comparator,
            right_operand=self._right_operand)


class TheInstructionArgumentsVariantConstructorForNotAndRelOpt(
    InstructionArgumentsVariantConstructorWithTemplateStringBase):
    """
    Constructs the instruction argument for a given expectation type config
    and rel-opt config.
    """

    def apply(self,
              etc: ExpectationTypeConfig,
              rel_opt_config: RelativityOptionConfiguration,
              ) -> str:
        ret_val = self.instruction_argument_template.replace('<rel_opt>', rel_opt_config.option_string)
        ret_val = replace_not_op(etc, ret_val)
        return ret_val


def replace_not_op(etc: ExpectationTypeConfig, s: str) -> str:
    return s.replace('<not_opt>', etc.nothing__if_positive__not_option__if_negative)


def instruction_arguments_for_emptiness_check(rel_opt: RelativityOptionConfiguration,
                                              file_name: str) -> str:
    complete_args = CompleteArgumentsConstructor(
        CommonArgumentsConstructor(file_name),
        EmptyAssertionVariant()
    )
    return complete_args.apply(ExpectationTypeConfig(ExpectationType.POSITIVE),
                               rel_opt)
