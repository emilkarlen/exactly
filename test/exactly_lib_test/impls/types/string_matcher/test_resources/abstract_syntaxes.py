from exactly_lib.definitions.primitives import matcher
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.abstract_syntax import StringMatcherAbsStx


class RunProgramAbsStx(StringMatcherAbsStx):
    def __init__(self, program: ProgramAbsStx):
        self._program = program

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(matcher.RUN_PROGRAM),
            TokenSequence.optional_new_line(),
            self._program.tokenization(),
        ])
