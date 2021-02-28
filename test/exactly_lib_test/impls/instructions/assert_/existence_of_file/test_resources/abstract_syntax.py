from typing import Optional

from exactly_lib.definitions import logic
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.impls.instructions.test_resources.abstract_syntax import InstructionArgsAbsStx
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.abstract_syntax import FileMatcherAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx


class InstructionArguments(InstructionArgsAbsStx):
    def __init__(self,
                 path: PathAbsStx,
                 expectation_type: ExpectationType = ExpectationType.POSITIVE,
                 file_matcher: Optional[FileMatcherAbsStx] = None,
                 ):
        self._path = path
        self._expectation_type = expectation_type
        self._file_matcher = file_matcher

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.optional_new_line(),
            self._expectation_type_tokens(),
            self._path.tokenization(),
            self._file_matcher_tokens()
        ])

    def _expectation_type_tokens(self) -> TokenSequence:
        return (
            TokenSequence.empty()
            if self._expectation_type is ExpectationType.POSITIVE
            else
            TokenSequence.sequence([
                logic.NOT_OPERATOR_NAME,
                layout.OPTIONAL_NEW_LINE,
            ])
        )

    def _file_matcher_tokens(self) -> TokenSequence:
        if not self._file_matcher:
            return TokenSequence.empty()
        else:
            return TokenSequence.concat([
                TokenSequence.singleton(':'),
                TokenSequence.optional_new_line(),
                self._file_matcher.tokenization(),
            ])
