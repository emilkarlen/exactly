from typing import Sequence

from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.sub_proc import sub_process_execution as spe
from exactly_lib.util.process_execution.os_process_execution import Command


class SubProcessExecutionSetup:
    def __init__(self,
                 cmd_and_args_resolver: spe.CommandResolver):
        self.cmd_and_args_resolver = cmd_and_args_resolver

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return self.cmd_and_args_resolver.symbol_usages

    def resolve_command(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return self.cmd_and_args_resolver.resolve(environment)


class ValidationAndSubProcessExecutionSetup(SubProcessExecutionSetup):
    def __init__(self,
                 validator: PreOrPostSdsValidator,
                 cmd_and_args_resolver: spe.CommandResolver):
        super().__init__(cmd_and_args_resolver)
        self.validator = validator


class ValidationAndSubProcessExecutionSetupParser:
    def parse(self, source: ParseSource) -> ValidationAndSubProcessExecutionSetup:
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            return self.parse_from_token_parser(parser)

    def parse_from_token_parser(self, parser: TokenParser) -> ValidationAndSubProcessExecutionSetup:
        raise NotImplementedError('abstract method')
