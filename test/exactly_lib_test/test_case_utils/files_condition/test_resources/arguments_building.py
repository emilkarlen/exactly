from typing import Optional, List, Sequence

from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_utils.files_condition import syntax
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements, Arguments
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer, Singleton
from exactly_lib_test.test_resources.strings import WithToString


class FileCondition:
    def __init__(self,
                 name: WithToString,
                 condition: Optional[FileMatcherArg] = None,
                 ):
        self.name = name
        self.condition = condition

    @property
    def as_argument_elements(self) -> ArgumentElements:
        fn = ArgumentElements([self.name])
        return (
            fn
            if self.condition is None
            else
            fn.followed_by(self.condition.as_argument_elements, [syntax.FILE_MATCHER_SEPARATOR])
        )


BEGIN_BRACE_RENDERER = Singleton(syntax.BEGIN_BRACE)

END_BRACE_RENDERER = Singleton(syntax.END_BRACE)


class FilesCondition(ArgumentElementsRenderer):
    def __init__(self, files: Sequence[FileCondition]):
        self.files = files

    @property
    def elements(self) -> List[WithToString]:
        raise NotImplementedError('unsupported')

    @property
    def as_str(self) -> str:
        return self.as_argument_elements.as_arguments.as_single_string

    @property
    def as_arguments(self) -> Arguments:
        return self.as_argument_elements.as_arguments

    @property
    def as_argument_elements(self) -> ArgumentElements:
        ret_val = ArgumentElements([syntax.BEGIN_BRACE])
        for fc in self.files:
            ret_val = ret_val.followed_by_lines(fc.as_argument_elements.all_lines)

        return ret_val.last_line_followed_by(ArgumentElements([syntax.END_BRACE]))

    @property
    def as_remaining_source(self) -> ParseSource:
        return self.as_argument_elements.as_remaining_source
