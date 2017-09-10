from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig


class InstructionArgumentsVariantConstructor:
    """"Constructs instruction arguments for a variant of (expectation type, any-or-every)."""

    def __init__(self,
                 regex_arg_str: str,
                 superfluous_args_str: str):
        self.regex_arg_str = regex_arg_str
        self.superfluous_args_str = superfluous_args_str

    def construct(self,
                  expectation_type: ExpectationType,
                  any_or_every_keyword: str,
                  ) -> str:
        superfluous_args_str = self.superfluous_args_str
        if superfluous_args_str:
            superfluous_args_str = ' ' + superfluous_args_str
        return '{maybe_not} {any_or_every} {line_matches} {regex}{superfluous_args_str}'.format(
            maybe_not=ExpectationTypeConfig(expectation_type).expectation_type_str,
            any_or_every=any_or_every_keyword,
            line_matches=instruction_options.LINE_ARGUMENT + ' ' + instruction_options.MATCHES_ARGUMENT,
            regex=self.regex_arg_str,
            superfluous_args_str=superfluous_args_str,
        )
