from typing import Sequence, List

from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.logic.program import stdin_data_sdv
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.symbol.logic.program.stdin_data_sdv import StdinDataSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.logic.string_transformers import StringTransformerSequenceSdv
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.sdv_with_validation import ObjectWithSymbolReferencesAndValidation
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import pre_or_post_validation
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator, \
    PreOrPostSdsValidatorFromValueValidator
from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.type_system.logic.program.stdin_data import StdinDataDdv
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv
from exactly_lib.util.symbol_table import SymbolTable


class ProgramElementsSdvAccumulator(ObjectWithSymbolReferencesAndValidation):
    """
    Helper class for handling elements that can be accumulated by a ProgramSdv
    """

    def __init__(self,
                 stdin: StdinDataSdv,
                 arguments: ArgumentsSdv,
                 transformations: Sequence[StringTransformerSdv],
                 validators: Sequence[PreOrPostSdsValidator]):
        self.stdin = stdin
        self.arguments = arguments
        self.transformations = transformations
        self.validators = list(validators) + self._validators_of_transformers(transformations)

    def new_accumulated(self,
                        additional_stdin: StdinDataSdv,
                        additional_arguments: ArgumentsSdv,
                        additional_transformations: Sequence[StringTransformerSdv],
                        additional_validation: Sequence[PreOrPostSdsValidator],
                        ) -> 'ProgramElementsSdvAccumulator':
        """Creates a new accumulated instance."""
        return ProgramElementsSdvAccumulator(self.stdin.new_accumulated(additional_stdin),
                                             self.arguments.new_accumulated(additional_arguments),
                                             tuple(self.transformations) + tuple(additional_transformations),
                                             tuple(self.validators) + tuple(additional_validation))

    @property
    def references(self) -> Sequence[SymbolReference]:
        objects_with_refs = [self.stdin, self.arguments] + list(self.transformations)
        return references_from_objects_with_symbol_references(objects_with_refs)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.all_of(self.validators)

    def resolve_stdin_data(self, symbols: SymbolTable) -> StdinDataDdv:
        return self.stdin.resolve_value(symbols)

    def resolve_transformations(self, symbols: SymbolTable) -> StringTransformerDdv:
        return StringTransformerSequenceSdv(self.transformations).resolve(symbols)

    @staticmethod
    def _validators_of_transformers(transformations: Sequence[StringTransformerSdv]
                                    ) -> List[PreOrPostSdsValidator]:
        return [
            PreOrPostSdsValidatorFromValueValidator(lambda symbols: transformation.resolve(symbols).validator())
            for transformation in transformations
        ]


def empty() -> ProgramElementsSdvAccumulator:
    return ProgramElementsSdvAccumulator(stdin_data_sdv.no_stdin(),
                                         arguments_sdvs.empty(),
                                         (),
                                         ())


def new_with_validators(validators: Sequence[PreOrPostSdsValidator]) -> ProgramElementsSdvAccumulator:
    return ProgramElementsSdvAccumulator(stdin_data_sdv.no_stdin(),
                                         arguments_sdvs.empty(),
                                         (),
                                         validators)


def new_with_arguments_and_validators(arguments: ListSdv,
                                      validators: Sequence[PreOrPostSdsValidator]) -> ProgramElementsSdvAccumulator:
    return ProgramElementsSdvAccumulator(stdin_data_sdv.no_stdin(),
                                         arguments_sdvs.new_without_validation(arguments),
                                         (),
                                         validators)


def new_with_arguments(arguments: ArgumentsSdv) -> ProgramElementsSdvAccumulator:
    return ProgramElementsSdvAccumulator(stdin_data_sdv.no_stdin(),
                                         arguments,
                                         (),
                                         ())
