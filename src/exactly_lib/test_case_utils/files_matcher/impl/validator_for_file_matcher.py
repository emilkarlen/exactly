from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.test_case import pre_or_post_validation as validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.util.symbol_table import SymbolTable


def resolver_validator_for_file_matcher(file_matcher: FileMatcherResolver) -> PreOrPostSdsValidator:
    def get_validator_of_selector(symbols: SymbolTable) -> validation.PreOrPostSdsValueValidator:
        return file_matcher.resolve(symbols).validator()

    return validation.PreOrPostSdsValidatorFromValueValidator(get_validator_of_selector)
