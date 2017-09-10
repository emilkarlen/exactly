from exactly_lib.help_texts.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.expectation_type import ExpectationType
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig


class InstructionArgumentsVariantConstructor:
    """"Constructs instruction arguments for a variant of (expectation type, any-or-every, transformer)."""

    def __init__(self,
                 regex_arg_str: str,
                 superfluous_args_str: str = '',
                 transformer: str = ''):
        self.transformer = transformer
        self.regex_arg_str = regex_arg_str
        self.superfluous_args_str = superfluous_args_str

    def construct(self,
                  expectation_type: ExpectationType,
                  any_or_every_keyword: str,
                  ) -> str:
        transformation = ''
        if self.transformer:
            transformation = option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME) + ' ' + self.transformer

        superfluous_args_str = self.superfluous_args_str
        if superfluous_args_str:
            superfluous_args_str = ' ' + superfluous_args_str

        return '{transformation} {maybe_not} {any_or_every} {line_matches} {regex}{superfluous_args_str}'.format(
            transformation=transformation,
            maybe_not=ExpectationTypeConfig(expectation_type).nothing__if_positive__not_option__if_negative,
            any_or_every=any_or_every_keyword,
            line_matches=instruction_options.LINE_ARGUMENT + ' ' + instruction_options.MATCHES_ARGUMENT,
            regex=self.regex_arg_str,
            superfluous_args_str=superfluous_args_str,
        )
