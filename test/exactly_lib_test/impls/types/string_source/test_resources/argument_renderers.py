from abc import ABC
from typing import List

from exactly_lib.definitions.primitives.string import HERE_DOCUMENT_MARKER_PREFIX
from exactly_lib.impls.types.string_source import defs as str_src_defs
from exactly_lib_test.tcfs.test_resources.path_arguments import PathArgument
from exactly_lib_test.test_resources import argument_renderer as args_rend
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString


class HereDocument(ArgumentElementsRenderer, ABC):
    def __init__(self, separator: str, contents_ended_w_new_line: str):
        self.separator = separator
        self.contents_ended_w_new_line = contents_ended_w_new_line

    @property
    def elements(self) -> List[WithToString]:
        return [HERE_DOCUMENT_MARKER_PREFIX + self.separator, '\n',
                self.contents_ended_w_new_line,
                self.separator]


class FileOrString(ArgumentElementsRenderer, ABC):
    @staticmethod
    def of_string(string: str) -> 'FileOrString':
        return FileOrStringAsString(string)

    @staticmethod
    def of_file(file: PathArgument) -> 'FileOrString':
        return FileOrStringAsFile(file)

    @staticmethod
    def of_here_doc(separator: str,
                    contents_ended_w_new_line: str,
                    ) -> 'FileOrString':
        return FileOrStringAsHereDoc(
            HereDocument(separator, contents_ended_w_new_line)
        )


class FileOrStringAsString(FileOrString):
    def __init__(self, string: str):
        self.string = string

    @property
    def elements(self) -> List[WithToString]:
        return [self.string]


class FileOrStringAsHereDoc(FileOrString):
    def __init__(self, here_document: HereDocument):
        self.here_document = here_document

    @property
    def elements(self) -> List[WithToString]:
        return self.here_document.elements


class FileOrStringAsFile(FileOrString):
    def __init__(self, file: PathArgument):
        self.file = file

    @property
    def elements(self) -> List[WithToString]:
        render = args_rend.SequenceOfArguments([
            args_rend.OptionArgument(str_src_defs.FILE_OPTION),
            self.file,
        ])
        return render.elements
