from exactly_lib_test.impls.types.string_matcher.test_resources.abstract_syntaxes import StringMatcherNegationAbsStx
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathAbsStx
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.abstract_syntax import StringMatcherAbsStx


class InstructionArgumentsAbsStx(AbstractSyntax):
    def __init__(self,
                 path: PathAbsStx,
                 matcher: StringMatcherAbsStx,
                 ):
        self._path = path
        self._matcher = matcher

    @staticmethod
    def of_optionally_negated(path: PathAbsStx,
                              matcher: StringMatcherAbsStx,
                              is_negated: bool,
                              ) -> 'InstructionArgumentsAbsStx':
        matcher = (
            StringMatcherNegationAbsStx(matcher)
            if is_negated
            else
            matcher
        )
        return InstructionArgumentsAbsStx(path, matcher)

    def tokenization(self) -> TokenSequence:
        return TokenSequence.concat([
            self._path.tokenization(),
            TokenSequence.optional_new_line(),
            self._matcher.tokenization(),
        ])
