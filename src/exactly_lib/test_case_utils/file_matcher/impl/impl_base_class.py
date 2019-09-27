from exactly_lib.test_case_utils.file_matcher.impl.combinators import FileMatcherNot
from exactly_lib.type_system.logic.file_matcher import FileMatcher


class FileMatcherImplBase(FileMatcher):
    @property
    def negation(self) -> FileMatcher:
        return FileMatcherNot(self)
