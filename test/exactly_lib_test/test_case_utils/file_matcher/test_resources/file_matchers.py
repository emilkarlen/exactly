from exactly_lib.test_case_utils.file_matcher import file_matchers as sut
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcher
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test


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
        raise HardErrorException(new_single_string_text_for_test(self.error_message))
