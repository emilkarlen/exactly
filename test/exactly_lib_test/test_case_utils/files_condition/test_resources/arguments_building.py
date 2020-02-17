from typing import Optional, List, Sequence

from exactly_lib.test_case_utils.files_condition import syntax
from exactly_lib.util.collection import intersperse_list
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer, Singleton, NEW_LINE, \
    SequenceOfArguments
from exactly_lib_test.test_resources.strings import WithToString


class FileCondition:
    def __init__(self,
                 name: WithToString,
                 condition: Optional[FileMatcherArg] = None,
                 ):
        self.name = name
        self.condition = condition

    @property
    def elements(self) -> List[WithToString]:
        ret_val = [str(self.name)]

        if self.condition:
            ret_val.append(syntax.FILE_MATCHER_SEPARATOR)
            ret_val += self.condition.elements

        return ret_val


BEGIN_BRACE_RENDERER = Singleton(syntax.BEGIN_BRACE)

END_BRACE_RENDERER = Singleton(syntax.END_BRACE)


class FilesCondition(ArgumentElementsRenderer):
    def __init__(self, files: Sequence[FileCondition]):
        self.files = files

    @property
    def elements(self) -> List[WithToString]:
        elements = (
                [BEGIN_BRACE_RENDERER] +
                list(self.files) +
                [END_BRACE_RENDERER]
        )

        separated_elements = SequenceOfArguments(intersperse_list(NEW_LINE, elements))
        return separated_elements.elements
