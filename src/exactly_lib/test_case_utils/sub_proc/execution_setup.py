from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import from_parse_source, \
    TokenParserPrime
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.sub_proc import sub_process_execution as spe


class SubProcessExecutionSetup:
    def __init__(self,
                 cmd_and_args_resolver: spe.CmdAndArgsResolver,
                 is_shell: bool):
        self.cmd_and_args_resolver = cmd_and_args_resolver
        self.is_shell = is_shell

    @property
    def symbol_usages(self) -> list:
        return self.cmd_and_args_resolver.symbol_usages


class ValidationAndSubProcessExecutionSetup(SubProcessExecutionSetup):
    def __init__(self,
                 validator: PreOrPostSdsValidator,
                 cmd_and_args_resolver: spe.CmdAndArgsResolver,
                 is_shell: bool):
        super().__init__(cmd_and_args_resolver, is_shell)
        self.validator = validator


class ValidationAndSubProcessExecutionSetupParser:
    def parse(self, source: ParseSource) -> ValidationAndSubProcessExecutionSetup:
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            return self.parse_from_token_parser(parser)

    def parse_from_token_parser(self, parser: TokenParserPrime) -> ValidationAndSubProcessExecutionSetup:
        raise NotImplementedError('abstract method')
