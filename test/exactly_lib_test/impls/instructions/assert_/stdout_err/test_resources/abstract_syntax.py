from abc import ABC

from exactly_lib.impls.instructions.assert_.utils.file_contents.stdout_stderr import OUTPUT_FROM_PROGRAM_OPTION_NAME
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.source.token_sequences import OptionWMandatoryValue
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.abstract_syntax import StringMatcherAbsStx


class StdoutErrAbsStx(AbstractSyntax, ABC):
    pass


class StdoutErrFromActAbsStx(StdoutErrAbsStx):
    def __init__(self, expectation: StringMatcherAbsStx):
        self._expectation = expectation

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.optional_new_line(),
            self._expectation.tokenization(),
        ])


class StdoutErrFromProgramAbsStx(StdoutErrAbsStx):
    def __init__(self,
                 program: ProgramAbsStx,
                 expectation: StringMatcherAbsStx,
                 ):
        self._program = program
        self._expectation = expectation

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.optional_new_line(),
            OptionWMandatoryValue.of_option_name(
                OUTPUT_FROM_PROGRAM_OPTION_NAME,
                self._program.tokenization(),
            ),
            TokenSequence.new_line(),
            self._expectation.tokenization(),
        ])
