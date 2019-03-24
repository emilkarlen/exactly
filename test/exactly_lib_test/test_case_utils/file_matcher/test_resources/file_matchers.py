from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib.type_system.error_message import ConstantErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcher
from exactly_lib.type_system.logic.hard_error import HardErrorException


class ConstantResultMatcher(sut.FileMatcher):
    def __init__(self, result: bool):
        self.result = result

    def matches(self, model: FileMatcherModel) -> bool:
        return self.result

    @property
    def option_description(self) -> str:
        return 'option description'


class FileMatcherThatReportsHardError(FileMatcher):
    def __init__(self, error_message: str = 'unconditional hard error'):
        self.error_message = error_message

    @property
    def option_description(self) -> str:
        return 'unconditional HARD ERROR'

    def matches(self, model: FileMatcherModel) -> bool:
        raise HardErrorException(ConstantErrorMessageResolver(self.error_message))
