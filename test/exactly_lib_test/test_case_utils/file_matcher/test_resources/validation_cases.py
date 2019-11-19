from typing import Sequence, List

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_utils.file_matcher import sdvs
from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherConstant
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherSymbolContext
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_value_validator import constant_validator
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationActual, \
    ValidationExpectationSvh
from exactly_lib_test.test_resources.name_and_value import NameAndValue


class ValidationCaseSvh:
    def __init__(self,
                 symbol_name: str,
                 expectation: ValidationExpectationSvh,
                 actual: ValidationActual,
                 ):
        def get_matcher(environment: PathResolvingEnvironmentPreOrPostSds) -> FileMatcher:
            return FileMatcherConstant(True)

        self._expectation = expectation
        self._symbol_context = FileMatcherSymbolContext(
            symbol_name,
            sdvs.FileMatcherSdvFromParts(
                [],
                validator=constant_validator(actual),
                matcher=get_matcher
            )
        )

    @property
    def transformer_arguments_string(self) -> str:
        return argument_syntax.syntax_for_transformer_option(
            self._symbol_context.name
        )

    @property
    def transformer_arguments_elements(self) -> List[str]:
        return argument_syntax.arguments_for_transformer_option(
            self._symbol_context.name
        )

    @property
    def symbol_context(self) -> FileMatcherSymbolContext:
        return self._symbol_context

    @property
    def expectation(self) -> ValidationExpectationSvh:
        return self._expectation


def failing_validation_cases__svh(symbol_name: str = 'file_matcher_symbol'
                                  ) -> Sequence[NameAndValue[ValidationCaseSvh]]:
    return [
        NameAndValue(
            case.name,
            ValidationCaseSvh(symbol_name,
                              case.expected,
                              case.actual)
        )
        for case in validation.failing_validation_cases__svh()
    ]
