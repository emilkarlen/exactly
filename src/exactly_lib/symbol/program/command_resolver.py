from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.symbol.resolver_with_validation import DirDepValueResolverWithValidation
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.symbol.utils import DirDepValueResolver
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.command import arguments_resolvers
from exactly_lib.type_system.logic.program.command_value import CommandValue, CommandDriverValue
from exactly_lib.util.process_execution.command import Command
from exactly_lib.util.symbol_table import SymbolTable


class CommandDriverResolver(DirDepValueResolver[CommandDriverValue]):
    """
    Resolves a :class:`CommandDriverValue`,
    and supplies a validator of the ingredients involved.
    """

    def __init__(self, validators: Sequence[PreOrPostSdsValidator] = ()):
        self._validators = validators

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return self._validators

    def resolve(self, symbols: SymbolTable) -> CommandDriverValue:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')


class CommandResolver(DirDepValueResolverWithValidation[CommandValue]):
    """
    Resolves a :class:`CommandValue`,
    and supplies a validator of the ingredients involved.

    This class works a bit like a immutable builder of Command - new arguments
    may be appended to form a new object representing a different command.

    This is the way more complex commands are built from simpler ones.
    """

    def __init__(self,
                 command_driver: CommandDriverResolver,
                 arguments: ArgumentsResolver):
        self._driver = command_driver
        self._arguments = arguments

    def new_with_additional_arguments(self, additional_arguments: ArgumentsResolver):
        """
        Creates a new resolver with additional arguments appended at the end of
        current argument list.

        :returns CommandResolver
        """
        return CommandResolver(self._driver,
                               self._arguments.new_accumulated(additional_arguments))

    def new_with_additional_argument_list(self, additional_arguments: ListResolver):
        return self.new_with_additional_arguments(arguments_resolvers.new_without_validation(additional_arguments))

    def resolve(self, symbols: SymbolTable) -> CommandValue:
        return CommandValue(self._driver.resolve(symbols),
                            self._arguments.arguments_list.resolve(symbols))

    def resolve_of_any_dep(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return self.resolve(environment.symbols).value_of_any_dependency(environment.home_and_sds)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.all_of(self.validators)

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return tuple(self._driver.validators) + tuple(self._arguments.validators)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([
            self._driver,
            self._arguments])

    @property
    def arguments(self) -> ListResolver:
        return self._arguments.arguments_list
