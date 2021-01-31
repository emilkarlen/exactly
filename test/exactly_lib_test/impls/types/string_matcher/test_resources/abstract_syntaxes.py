from exactly_lib.definitions.primitives import matcher
from exactly_lib.impls.types.string_matcher import matcher_options
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.abstract_syntax import StringMatcherAbsStx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx


class RunProgramAbsStx(StringMatcherAbsStx):
    def __init__(self, program: ProgramAbsStx):
        self._program = program

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(matcher.RUN_PROGRAM),
            TokenSequence.optional_new_line(),
            self._program.tokenization(),
        ])


class EqualsAbsStx(StringMatcherAbsStx):
    def __init__(self, expected: StringSourceAbsStx):
        self._expected = expected

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            TokenSequence.singleton(matcher_options.EQUALS_ARGUMENT),
            TokenSequence.optional_new_line(),
            self._expected.tokenization(),
        ])
