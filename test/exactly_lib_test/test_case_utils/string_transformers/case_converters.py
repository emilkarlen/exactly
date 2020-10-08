import unittest

from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import case_converters as tr
from exactly_lib_test.test_case_utils.string_transformers.test_resources.case_converters import CaseConverterConfig


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestToUpper),
        unittest.makeSuite(TestToLower),
    ])


class TestToLower(tr.CaseConverterTestBase):
    @property
    def config(self) -> CaseConverterConfig:
        return CaseConverterConfig(
            args.to_lower_case(),
            str.lower,
        )


class TestToUpper(tr.CaseConverterTestBase):
    @property
    def config(self) -> CaseConverterConfig:
        return CaseConverterConfig(
            args.to_upper_case(),
            str.upper,
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
