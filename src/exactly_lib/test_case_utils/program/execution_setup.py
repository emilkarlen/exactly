from typing import Sequence

from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.command_resolver import CommandResolver


class NewCommandResolverAndStdin:
    def __init__(self,
                 validator: PreOrPostSdsValidator,
                 command_resolver: CommandResolver):
        self._command_resolver = command_resolver
        self._validator = validator

    @property
    def symbol_usages(self) -> Sequence[SymbolReference]:
        return self._command_resolver.references

    @property
    def command_resolver(self) -> CommandResolver:
        return self._command_resolver

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator


class NewCommandResolverAndStdinParser:
    def parse(self, source: ParseSource) -> NewCommandResolverAndStdin:
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            return self.parse_from_token_parser(parser)

    def parse_from_token_parser(self, parser: TokenParser) -> NewCommandResolverAndStdin:
        raise NotImplementedError('abstract method')
