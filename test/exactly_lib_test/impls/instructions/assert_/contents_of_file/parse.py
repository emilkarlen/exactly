import unittest

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.assert_.contents_of_file.test_resources.abstract_syntax import \
    InstructionArgumentsAbsStx
from exactly_lib_test.impls.instructions.assert_.contents_of_file.test_resources.instruction_check import PARSE_CHECKER
from exactly_lib_test.impls.types.expression.test_resources.test_grammars import \
    NOT_A_PRIMITIVE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_resources.source.abstract_syntax_impls import CustomAbsStx
from exactly_lib_test.test_resources.source.custom_abstract_syntax import SequenceAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntaxes import DefaultRelPathAbsStx
from exactly_lib_test.type_val_deps.types.string_matcher.test_resources.abstract_syntax import \
    StringMatcherSymbolReferenceAbsStx


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestParse)


class TestParse(unittest.TestCase):
    def test_raise_exception_when_syntax_is_invalid(self):
        source_cases = [
            NameAndValue(
                'empty - missing all arguments',
                CustomAbsStx.empty(),
            ),
            NameAndValue(
                'superfluous arguments',
                SequenceAbsStx.followed_by_superfluous(
                    InstructionArgumentsAbsStx(
                        DefaultRelPathAbsStx('actual.txt'),
                        StringMatcherSymbolReferenceAbsStx('STRING_MATCHER'),
                    )
                ),
            ),
            NameAndValue(
                'invalid matcher',
                SequenceAbsStx.followed_by_superfluous(
                    InstructionArgumentsAbsStx(
                        DefaultRelPathAbsStx('actual.txt'),
                        StringMatcherSymbolReferenceAbsStx(
                            NOT_A_PRIMITIVE_EXPR_NAME_AND_NOT_A_VALID_SYMBOL_NAME
                        ),
                    )
                ),
            )
        ]
        for source_case in source_cases:
            with self.subTest(source_case.name):
                PARSE_CHECKER.check_invalid_syntax__src_var_consume_last_line_abs_stx(
                    self,
                    source_case.value,
                )
