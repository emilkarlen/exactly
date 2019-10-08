from exactly_lib.type_system.logic.file_matcher import FileMatcherModel, FileMatcher
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib_test.common.test_resources.text_doc_assertions import new_single_string_text_for_test


def arbitrary_file_matcher() -> FileMatcher:
    return ConstantResultMatcher(True)


class ConstantResultMatcher(FileMatcher):
    def __init__(self, result: bool):
        super().__init__()
        self.result = result

    @property
    def name(self) -> str:
        return 'constant ' + str(self.result)

    @property
    def option_description(self) -> str:
        return 'option description'

    def negation(self) -> FileMatcher:
        return ConstantResultMatcher(not self.result)

    def matches(self, model: FileMatcherModel) -> bool:
        return self.result

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return self._new_tb().build_result(self.result)


class FileMatcherConstantWithName(FileMatcher):
    def __init__(self, name: str, result: bool):
        super().__init__()
        self._name = name
        self._result = result

    @property
    def result_constant(self) -> bool:
        return self._result

    @property
    def name(self) -> str:
        return self._name

    @property
    def option_description(self) -> str:
        return self._name

    @property
    def negation(self) -> FileMatcher:
        return FileMatcherConstantWithName('not ' + self._name,
                                           not self._result)

    def matches(self, model: FileMatcherModel) -> bool:
        return self._result

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return self._new_tb().build_result(self._result)


class FileMatcherThatReportsHardError(FileMatcher):
    def __init__(self, error_message: str = 'unconditional hard error'):
        super().__init__()
        self.error_message = error_message

    @property
    def name(self) -> str:
        return str(type(self))

    @property
    def option_description(self) -> str:
        return 'unconditional HARD ERROR'

    @property
    def negation(self) -> FileMatcher:
        return self

    def matches(self, model: FileMatcherModel) -> bool:
        raise HardErrorException(new_single_string_text_for_test(self.error_message))

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        raise HardErrorException(new_single_string_text_for_test(self.error_message))