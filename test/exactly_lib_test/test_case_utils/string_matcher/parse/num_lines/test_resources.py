from exactly_lib.definitions.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.test_case_utils.string_matcher import matcher_options
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import \
    nothing__if_positive__not_option__if_negative


class InstructionArgumentsVariantConstructor:
    """"Constructs instruction arguments for a variant of (TRANSFORMER, [!]  OPERATOR OPERAND)."""

    def __init__(self,
                 operator: str,
                 operand: str,
                 superfluous_args_str: str = '',
                 transformer: str = ''):
        self.transformer = transformer
        self.operator = operator
        self.operand = operand
        self.superfluous_args_str = superfluous_args_str

    def construct(self, expectation_type: ExpectationType) -> str:
        transformation = ''
        if self.transformer:
            transformation = option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME) + ' ' + self.transformer

        superfluous_args_str = self.superfluous_args_str
        if superfluous_args_str:
            superfluous_args_str = ' ' + superfluous_args_str

        return '{transformation} {maybe_not} {num_lines} {operator} {operand}{superfluous_args_str}'.format(
            transformation=transformation,
            maybe_not=nothing__if_positive__not_option__if_negative(expectation_type),
            num_lines=matcher_options.NUM_LINES_ARGUMENT,
            operator=self.operator,
            operand=self.operand,
            superfluous_args_str=superfluous_args_str,
        )
