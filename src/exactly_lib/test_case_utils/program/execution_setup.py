from typing import Sequence

from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.command.new_command_resolver import NewCommandResolver
from exactly_lib.test_case_utils.program.command_resolver import CommandResolver
from exactly_lib.util.process_execution.os_process_execution import Command


class CommandResolverAndStdin(ObjectWithTypedSymbolReferences):
    """
    TODO Replace hierarchy with a single class when done
    """

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    @property
    def command_resolver(self) -> CommandResolver:
        return None

    @property
    def new_command_resolver(self) -> NewCommandResolver:
        return None

    def resolve_command(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        raise NotImplementedError('abstract method')

    @property
    def validator(self) -> PreOrPostSdsValidator:
        raise NotImplementedError('abstract method')


class OldCommandResolverAndStdin(CommandResolverAndStdin):
    def __init__(self,
                 validator: PreOrPostSdsValidator,
                 command_resolver: CommandResolver):
        self._command_resolver = command_resolver
        self._validator = validator

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._command_resolver.references

    @property
    def command_resolver(self) -> CommandResolver:
        return self._command_resolver

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    def resolve_command(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return self._command_resolver.resolve(environment)


class NewCommandResolverAndStdin(CommandResolverAndStdin):
    def __init__(self, command_resolver: NewCommandResolver):
        self._command_resolver = command_resolver

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._command_resolver.references

    @property
    def new_command_resolver(self) -> NewCommandResolver:
        return self._command_resolver

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._command_resolver.validator

    def resolve_command(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return self._command_resolver.resolve(environment)


class NewCommandResolverAndStdinParser:
    def parse(self, source: ParseSource) -> NewCommandResolverAndStdin:
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            return self.parse_from_token_parser(parser)

    def parse_from_token_parser(self, parser: TokenParser) -> NewCommandResolverAndStdin:
        raise NotImplementedError('abstract method')
