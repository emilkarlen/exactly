from typing import Sequence

from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils import pre_or_post_validation
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.sym_ref_and_validation import ObjectWithSymbolReferencesAndValidation
from exactly_lib.util.process_execution.os_process_execution import Command


class CommandDriverResolver(ObjectWithTypedSymbolReferences):
    """
    Represents one variant of :class:`Command`,
    and is thus responsible for construct a :class:`Command` given
    the arguments to the program.

    E.g., knows that for a shell command line, the arguments
    should be concatenated, separated by space, to a single string.

    There should probably exist one sub class per variant of
    :class:`Command` (shell, executable file, OS command).
    """

    def __init__(self, validators: Sequence[PreOrPostSdsValidator] = ()):
        self._validators = validators

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return self._validators

    def resolve(self,
                environment: PathResolvingEnvironmentPreOrPostSds,
                arguments: ListResolver) -> Command:
        raise NotImplementedError('abstract method')


class ArgumentsResolver(ObjectWithTypedSymbolReferences):
    def __init__(self,
                 arguments: ListResolver,
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        self._arguments = arguments
        self._validators = validators

    @property
    def arguments_list(self) -> ListResolver:
        return self._arguments

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return self._validators

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._arguments.references

    def new_with_appended(self,
                          arguments: ListResolver,
                          validators: Sequence[PreOrPostSdsValidator] = ()):
        args = list_resolvers.concat([self.arguments_list, arguments])
        validators = tuple(self._validators) + tuple(validators)

        return ArgumentsResolver(args, validators)


class CommandResolver(ObjectWithSymbolReferencesAndValidation):
    """
    Resolves a :class:`Command`,
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

    def new_with_additional_arguments(self,
                                      additional_arguments: ListResolver,
                                      additional_validation: Sequence[PreOrPostSdsValidator] = ()):
        """
        Creates a new resolver with additional arguments appended at the end of
        current argument list.

        :returns CommandResolver
        """
        return CommandResolver(self._driver,
                               self._arguments.new_with_appended(additional_arguments,
                                                                 additional_validation))

    def resolve(self, environment: PathResolvingEnvironmentPreOrPostSds) -> Command:
        return self.driver.resolve(environment, self._arguments.arguments_list)

    @property
    def driver(self) -> CommandDriverResolver:
        return self._driver

    @property
    def arguments(self) -> ListResolver:
        return self._arguments.arguments_list

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.all_of(tuple(self._driver.validators) +
                                             tuple(self._arguments.validators))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([
            self._driver,
            self._arguments])
