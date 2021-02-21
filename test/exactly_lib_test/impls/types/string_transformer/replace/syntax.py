import unittest

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.line_matcher.test_resources.abstract_syntaxes import LineMatcherInfixOpAbsStx
from exactly_lib_test.impls.types.string_transformer.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformer.test_resources.abstract_syntaxes import ReplaceRegexAbsStx
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_resources.source import abs_stx_utils
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources.abstract_syntax import \
    LineMatcherSymbolReferenceAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestMissingArguments(),
        TestLineMatcherShouldBeParsedAsSimpleExpr(),
    ])


class TestMissingArguments(unittest.TestCase):
    def runTest(self):
        line_filter_cases = [
            NameAndValue('wo line filter', None),
            NameAndValue('w line filter', LineMatcherSymbolReferenceAbsStx('LM_SYMBOL')),
        ]
        for line_filter_case in line_filter_cases:
            for preserve_new_lines in [False, True]:
                cases = [
                    NameAndValue(
                        'missing regex',
                        ReplaceRegexAbsStx.of_str('',
                                                  'replacement',
                                                  preserve_new_lines=preserve_new_lines,
                                                  lines_filter=line_filter_case.value,
                                                  ),
                    ),
                    NameAndValue(
                        'missing replacement',
                        ReplaceRegexAbsStx.of_str('regex',
                                                  '',
                                                  preserve_new_lines=preserve_new_lines,
                                                  lines_filter=line_filter_case.value,
                                                  ),
                    ),
                    NameAndValue(
                        'missing regex and replacement',
                        ReplaceRegexAbsStx.of_str('',
                                                  '',
                                                  preserve_new_lines=preserve_new_lines,
                                                  lines_filter=line_filter_case.value,
                                                  ),
                    ),
                ]
                for case in cases:
                    with self.subTest(case.name,
                                      preserve_new_lines=preserve_new_lines,
                                      lines_filter=line_filter_case.name):
                        integration_check.PARSE_CHECKER__FULL.check_invalid_syntax__abs_stx(
                            self,
                            case.value,
                        )


class TestLineMatcherShouldBeParsedAsSimpleExpr(unittest.TestCase):
    def runTest(self):
        # ARRANGE "
        lm_op_1 = LineMatcherSymbolReferenceAbsStx('LM_1')
        lm_op_2 = LineMatcherSymbolReferenceAbsStx('LM_2')
        line_matcher_w_infix_op = LineMatcherInfixOpAbsStx.conjunction([
            lm_op_1,
            lm_op_2,
        ])
        valid_regex = 'valid_regex'
        syntax = ReplaceRegexAbsStx.of_str(valid_regex,
                                           'valid_replacement',
                                           preserve_new_lines=False,
                                           lines_filter=line_matcher_w_infix_op,
                                           )
        for source_format_case in abs_stx_utils.formatting_cases(syntax):
            with self.subTest(formatting=source_format_case.name):
                source = remaining_source(source_format_case.value)
                # ACT #
                integration_check.PARSE_CHECKER__FULL.check_valid_arguments(
                    self,
                    source,
                )
                # ASSERT #
                remaining_non_space_source_str = source.remaining_source.lstrip()
                self.assertTrue(
                    remaining_non_space_source_str.startswith(valid_regex)
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
