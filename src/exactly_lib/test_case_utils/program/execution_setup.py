from typing import Sequence

from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.command.new_command_resolver import CommandResolver


class CommandResolverAndStdin(ObjectWithTypedSymbolReferences):
    """
    A command together with stdin contents.

    NOTE: The stdin contents component is not impl yet - but is
    mentioned in the name of the class to make the future purpose clear.
    """

    def __init__(self, command_resolver: CommandResolver):
        self._command_resolver = command_resolver

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._command_resolver.references

    @property
    def command_resolver(self) -> CommandResolver:
        return self._command_resolver

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._command_resolver.validator


class NewCommandResolverAndStdinParser:
    def parse(self, source: ParseSource) -> CommandResolverAndStdin:
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            return self.parse_from_token_parser(parser)

    def parse_from_token_parser(self, parser: TokenParser) -> CommandResolverAndStdin:
        raise NotImplementedError('abstract method')
