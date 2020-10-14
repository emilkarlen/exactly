import unittest
from typing import List

from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import may_dep_on_ext_resources


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(),
    ])


class TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(
    may_dep_on_ext_resources.TestMayDepOnExtResourcesShouldBeThatOfSourceModelBase):
    def argument_cases(self) -> List[str]:
        return [
            args.filter_line_nums('72').as_str,
            args.filter_line_nums('-72').as_str,
        ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
