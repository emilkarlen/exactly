from typing import Sequence

from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils import pre_or_post_validation
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.util.process_execution.os_process_execution import Command


class NewCommandDriverResolver(ObjectWithTypedSymbolReferences):
    """
    Represents one variant of :class:`Command`,
    and is thus responsible for construct a :class:`Command` given
    the arguments to the program.

    E.g., knows that for a shell command line, the arguments
    should be concatenated, separated by space, to a single string.

    There should probably exist one sub class per variant of
    :class:`Command` (shell, executable file, OS command).
    """

    def resolve(self,
                environment: PathResolvingEnvironmentPreOrPostSds,
                arguments: ListResolver) -> Command:
        raise NotImplementedError('abstract method')


class NewCommandResolver(ObjectWithTypedSymbolReferences):
    """
    Responsible for resolving a :class:`Command`,
    and validation of
    """

    def __init__(self,
                 command_driver: NewCommandDriverResolver,
                 arguments: ListResolver,
                 validator: PreOrPostSdsValidator):
        self._driver = command_driver
        self._arguments = arguments
        self._validator = validator

    @property
    def driver(self) -> NewCommandDriverResolver:
        return self._driver

    @property
    def arguments(self) -> ListResolver:
        return self._arguments

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._validator

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([
            self._driver,
            self._arguments])


# D
def append_arguments_wip(existing: NewCommandResolver,
                         additional_arguments: ListResolver,
                         additional_validation: PreOrPostSdsValidator,
                         ) -> NewCommandResolver:
    return NewCommandResolver(existing.driver,
                              list_resolvers.concat([existing.arguments, additional_arguments]),
                              pre_or_post_validation.all_of([existing.validator,
                                                             additional_validation])
                              )
