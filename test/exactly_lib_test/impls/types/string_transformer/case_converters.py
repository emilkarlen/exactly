import unittest
from typing import List

from exactly_lib_test.impls.types.string_transformer.test_resources import argument_syntax as args
from exactly_lib_test.impls.types.string_transformer.test_resources import case_converters as tr
from exactly_lib_test.impls.types.string_transformer.test_resources import may_dep_on_ext_resources
from exactly_lib_test.impls.types.string_transformer.test_resources.case_converters import CaseConverterConfig


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestToUpper),
        unittest.makeSuite(TestToLower),
        TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(),
    ])


class TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(
    may_dep_on_ext_resources.TestMayDepOnExtResourcesShouldBeThatOfSourceModelBase):
    def argument_cases(self) -> List[str]:
        return [args.to_lower_case(),
                args.to_upper_case()]


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
