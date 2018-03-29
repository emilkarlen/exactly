from exactly_lib.help_texts import instruction_arguments
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data import list_resolvers
from exactly_lib.test_case_utils.external_program.command import command_resolvers
from exactly_lib.test_case_utils.external_program.command_and_stdin import CommandAndStdinResolver
from exactly_lib.test_case_utils.external_program.parse import CommandAndStdinResolverParser
from exactly_lib.test_case_utils.parse.parse_string import string_resolver_from_string


class ShellCommandSetupParser(CommandAndStdinResolverParser):
    def parse_from_token_parser(self, parser: TokenParser) -> CommandAndStdinResolver:
        parser.require_is_not_at_eol('Missing {COMMAND}',
                                     _PARSE_FORMAT_MAP)
        argument_string = parser.consume_current_line_as_plain_string()
        argument = string_resolver_from_string(argument_string)

        if not argument_string:
            msg = instruction_arguments.COMMAND_ARGUMENT.name + ' must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)

        command_resolver = command_resolvers.for_shell()
        command_resolver = command_resolver.new_with_additional_arguments(list_resolvers.from_string(argument))

        return CommandAndStdinResolver(command_resolver)


_PARSE_FORMAT_MAP = {
    'COMMAND': instruction_arguments.COMMAND_ARGUMENT.name
}
