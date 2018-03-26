from typing import Sequence

from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.util.process_execution.os_process_execution import Command


class NewCommandDriverResolver(ObjectWithTypedSymbolReferences):

    def resolve(self,
                environment: PathResolvingEnvironmentPreOrPostSds,
                arguments: ListResolver) -> Command:
        raise NotImplementedError('abstract method')


class NewCommandResolver(ObjectWithTypedSymbolReferences):
    def __init__(self,
                 command_driver: NewCommandDriverResolver,
                 arguments: ListResolver,
                 validator: PreOrPostSdsValidator):
        self._driver = command_driver
        self._arguments = arguments
        self._validator = validator

    @property
    def driver_resolver(self) -> NewCommandDriverResolver:
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
