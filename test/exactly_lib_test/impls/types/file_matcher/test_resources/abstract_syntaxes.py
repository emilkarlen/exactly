from abc import ABC

from exactly_lib.definitions.primitives import file_matcher
from exactly_lib_test.test_resources.source import abstract_syntax_impls as abstract_syntaxes
from exactly_lib_test.test_resources.source import token_sequences
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.abstract_syntax import FileMatcherAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx


class PathArgumentPositionAbsStx(AbstractSyntax, ABC):
    pass


class PathArgumentPositionDefault(PathArgumentPositionAbsStx):
    def tokenization(self) -> TokenSequence:
        return TokenSequence.empty()


class PathArgumentPositionLast(PathArgumentPositionAbsStx):
    def tokenization(self) -> TokenSequence:
        return token_sequences.Option.of_option_name(file_matcher.PROGRAM_ARG_OPTION__LAST.name)


class PathArgumentPositionMarker(PathArgumentPositionAbsStx):
    def __init__(self, marker: str):
        self.marker = marker

    def tokenization(self) -> TokenSequence:
        return token_sequences.OptionWMandatoryValue.of_option_name(
            file_matcher.PROGRAM_ARG_OPTION__MARKER.name,
            TokenSequence.singleton(self.marker)
        )


class RunProgramAbsStx(FileMatcherAbsStx):
    def __init__(self,
                 program: ProgramAbsStx,
                 path_argument_position: PathArgumentPositionAbsStx,
                 ):
        self._program = program
        self._path_argument_position = path_argument_position

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(file_matcher.PROGRAM_MATCHER_NAME),
            TokenSequence.optional_new_line(),
            abstract_syntaxes.OptionallyOnNewLine(self._path_argument_position).tokenization(),
            self._program.tokenization(),
        ])
