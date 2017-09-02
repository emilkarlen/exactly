import unittest

from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.type_system import utils as sut
from exactly_lib_test.test_case_file_structure.test_resources_test.dir_dependent_value import AMultiDirDependentValue


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestResolvingDependenciesFromList)


class TestResolvingDependenciesFromList(unittest.TestCase):
    def test(self):
        cases = [
            (
                'empty sequence',
                [],
                set(),
            ),
            (
                'single value without dependencies',
                [AMultiDirDependentValue(resolving_dependencies=set())],
                set(),
            ),
            (
                'single value with single dependency',
                [AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.HOME})],
                {ResolvingDependency.HOME},
            ),
            (
                'multiple values with same dependency',
                [AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.NON_HOME}),
                 AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.NON_HOME})],
                {ResolvingDependency.NON_HOME},
            ),
        ]
        for test_case_name, dir_dependent_values, expected_dependencies in cases:
            with self.subTest(name=test_case_name):
                # ACT #
                actual = sut.resolving_dependencies_from_sequence(dir_dependent_values)
                # ASSERT #
                self.assertEqual(expected_dependencies, actual)
