import unittest
from typing import List

from exactly_lib_test.impls.types.string_transformer.test_resources import may_dep_on_ext_resources
from exactly_lib_test.impls.types.string_transformer.test_resources.abstract_syntaxes import ReplaceRegexAbsStx


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestMayDependOnExternalResourcesShouldBeThatOfSourceModelWhenNoLinesSelection(),
    ])


class TestMayDependOnExternalResourcesShouldBeThatOfSourceModelWhenNoLinesSelection(
    may_dep_on_ext_resources.TestMayDepOnExtResourcesShouldBeThatOfSourceModelBase):
    def argument_cases(self) -> List[str]:
        return [
            syntax.as_str__default()
            for syntax in [
                ReplaceRegexAbsStx.of_str('regex', 'replacement', False, None),
                ReplaceRegexAbsStx.of_str('regex', 'replacement', True, None),
            ]
        ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
