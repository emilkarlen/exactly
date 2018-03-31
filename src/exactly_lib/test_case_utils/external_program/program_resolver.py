from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils import pre_or_post_validation
from exactly_lib.test_case_utils.external_program.command.command_resolver import CommandResolver
from exactly_lib.test_case_utils.external_program.component_resolvers import StdinDataResolver
from exactly_lib.test_case_utils.external_program.program import ProgramValue
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerSequenceResolver
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.resolver_with_validation import DirDepValueResolverWithValidation
from exactly_lib.util.symbol_table import SymbolTable


class ProgramResolver(DirDepValueResolverWithValidation[ProgramValue]):
    def __init__(self,
                 command: CommandResolver,
                 stdin: StdinDataResolver,
                 transformations: Sequence[LinesTransformerResolver] = ()
                 ):
        self._stdin = stdin
        self._command = command
        self._transformations = transformations

    def new_with_additional_arguments(self,
                                      additional_arguments: ListResolver,
                                      additional_validation: Sequence[PreOrPostSdsValidator] = ()):
        """
        Creates a new resolver with additional arguments appended at the end of
        current argument list.
        """
        return ProgramResolver(
            self._command.new_with_additional_arguments(additional_arguments,
                                                        additional_validation),
            self._stdin,
            self._transformations)

    def new_with_additional_transformations(self, transformations: Sequence[LinesTransformerResolver]):
        """
        Creates a new resolver with additional transformation appended at the end of
        current transformations.
        """
        return ProgramResolver(
            self._command,
            self._stdin,
            tuple(self._transformations) + tuple(transformations))

    @property
    def references(self) -> Sequence[SymbolReference]:
        objects_with_refs = [self._command, self._stdin] + list(self._transformations)
        return references_from_objects_with_symbol_references(objects_with_refs)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.all_of(self.validators)

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return tuple(self._command.validators) + tuple(self._stdin.validators)

    def resolve_value(self, symbols: SymbolTable) -> ProgramValue:
        return ProgramValue(self._command.resolve_value(symbols),
                            self._stdin.resolve_value(symbols),
                            LinesTransformerSequenceResolver(self._transformations).resolve(symbols))
