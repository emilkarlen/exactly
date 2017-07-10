import unittest

from exactly_lib.test_case_file_structure import dir_dependent_value as sut
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencies
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDirDependencyOfResolvingDependencies),
    ])


class TestDirDependencyOfResolvingDependencies(unittest.TestCase):
    def runTest(self):
        cases = [
            (
                set(),
                DirDependencies.NONE,
            ),
            (
                {ResolvingDependency.HOME},
                DirDependencies.HOME,
            ),
            (
                {ResolvingDependency.NON_HOME},
                DirDependencies.SDS,
            ),
            (
                {ResolvingDependency.HOME,
                 ResolvingDependency.NON_HOME},
                DirDependencies.HOME_AND_SDS,
            ),
        ]
        for resolving_dependencies, expected_dir_dependency in cases:
            with self.subTest(resolving_dependencies=resolving_dependencies,
                              expected_dir_dependency=expected_dir_dependency):
                actual = sut.dir_dependency_of_resolving_dependencies(resolving_dependencies)
                self.assertEqual(expected_dir_dependency,
                                 actual)
