from exactly_lib.help_texts import instruction_arguments
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case_utils.parse.parse_string import string_resolver_from_string
from exactly_lib.test_case_utils.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.test_case_utils.sub_proc.cmd_and_args_resolvers import ConstantCmdAndArgsResolver
from exactly_lib.test_case_utils.sub_proc.execution_setup import ValidationAndSubProcessExecutionSetupParser, \
    ValidationAndSubProcessExecutionSetup


class ShellCommandSetupParser(ValidationAndSubProcessExecutionSetupParser):
    def parse_from_token_parser(self, parser: TokenParser) -> ValidationAndSubProcessExecutionSetup:
        parser.require_is_not_at_eol('Missing {COMMAND}',
                                     _PARSE_FORMAT_MAP)
        argument_string = parser.consume_current_line_as_plain_string()
        argument = string_resolver_from_string(argument_string)
        if not argument_string:
            msg = instruction_arguments.COMMAND_ARGUMENT.name + ' must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)
        return ValidationAndSubProcessExecutionSetup(
            ConstantSuccessValidator(),
            ConstantCmdAndArgsResolver(argument),
            is_shell=True)


_PARSE_FORMAT_MAP = {
    'COMMAND': instruction_arguments.COMMAND_ARGUMENT.name
}
