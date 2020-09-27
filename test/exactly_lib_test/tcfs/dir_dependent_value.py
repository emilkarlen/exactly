import unittest

from exactly_lib.tcfs import dir_dependent_value as sut
from exactly_lib.tcfs.dir_dependent_value import DirDependencies
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition


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
                {DirectoryStructurePartition.HDS},
                DirDependencies.HDS,
            ),
            (
                {DirectoryStructurePartition.NON_HDS},
                DirDependencies.SDS,
            ),
            (
                {DirectoryStructurePartition.HDS,
                 DirectoryStructurePartition.NON_HDS},
                DirDependencies.TCDS,
            ),
        ]
        for resolving_dependencies, expected_dir_dependency in cases:
            with self.subTest(resolving_dependencies=resolving_dependencies,
                              expected_dir_dependency=expected_dir_dependency):
                actual = sut.dir_dependency_of_resolving_dependencies(resolving_dependencies)
                self.assertEqual(expected_dir_dependency,
                                 actual)
