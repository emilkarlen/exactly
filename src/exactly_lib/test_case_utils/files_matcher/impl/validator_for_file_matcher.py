from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.test_case.validation import sdv_validation as validation
from exactly_lib.test_case.validation.sdv_validation import SdvValidator
from exactly_lib.util.symbol_table import SymbolTable


def sdv_validator_for_file_matcher(file_matcher: FileMatcherSdv) -> SdvValidator:
    def get_validator_of_selector(symbols: SymbolTable) -> validation.DdvValidator:
        return file_matcher.resolve(symbols).validator()

    return validation.SdvValidatorFromDdvValidator(get_validator_of_selector)
