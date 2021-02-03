import unittest

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.abstract_syntax import \
    InstructionArguments
from exactly_lib_test.impls.instructions.assert_.process_output.exit_code.test_resources.instruction_check import \
    PARSE_CHECKER
from exactly_lib_test.impls.types.integer_matcher.test_resources import abstract_syntaxes as im_abs_stx
from exactly_lib_test.impls.types.integer_matcher.test_resources.abstract_syntaxes import CustomIntegerMatcherAbsStx
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.abstract_syntax import \
    IntegerMatcherSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import CustomPgmAndArgsAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestInvalidSyntax(),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def runTest(self):
        cases = [
            NameAndValue(
                'missing int matcher',
                InstructionArguments(
                    ProgramOfSymbolReferenceAbsStx('PROGRAM_SYMBOL'),
                    CustomIntegerMatcherAbsStx.empty(),
                ),
            ),
            NameAndValue(
                'missing program',
                InstructionArguments(
                    CustomPgmAndArgsAbsStx.empty(),
                    IntegerMatcherSymbolReferenceAbsStx('INT_MATCHER_SYMBOL'),
                ),
            ),
            NameAndValue(
                'superfluous arguments',
                InstructionArguments(
                    ProgramOfSymbolReferenceAbsStx('PROGRAM_SYMBOL'),
                    im_abs_stx.symbol_reference_followed_by_superfluous_string_on_same_line('INT_MATCHER_SYMBOL'),
                ),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                PARSE_CHECKER.check_invalid_syntax__abs_stx(
                    self,
                    case.value,
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
