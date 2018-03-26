from exactly_lib.help_texts import instruction_arguments
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data import list_resolvers
from exactly_lib.test_case_utils.parse.parse_string import string_resolver_from_string
from exactly_lib.test_case_utils.program.command import new_command_resolvers
from exactly_lib.test_case_utils.program.execution_setup import NewCommandResolverAndStdinParser, \
    CommandResolverAndStdin


class ShellCommandSetupParser(NewCommandResolverAndStdinParser):
    def parse_from_token_parser(self, parser: TokenParser) -> CommandResolverAndStdin:
        parser.require_is_not_at_eol('Missing {COMMAND}',
                                     _PARSE_FORMAT_MAP)
        argument_string = parser.consume_current_line_as_plain_string()
        argument = string_resolver_from_string(argument_string)

        if not argument_string:
            msg = instruction_arguments.COMMAND_ARGUMENT.name + ' must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)

        command_resolver = new_command_resolvers.for_shell()
        command_resolver = command_resolver.new_with_additional_arguments(list_resolvers.from_string(argument))

        return CommandResolverAndStdin(command_resolver)


_PARSE_FORMAT_MAP = {
    'COMMAND': instruction_arguments.COMMAND_ARGUMENT.name
}
