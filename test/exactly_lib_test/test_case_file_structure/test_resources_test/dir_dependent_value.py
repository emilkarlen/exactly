import pathlib
import unittest
from typing import Set, Generic, Callable, Optional

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencies, \
    dir_dependency_of_resolving_dependencies, RESOLVED_TYPE
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_case_file_structure.test_resources import dir_dependent_value as sut
from exactly_lib_test.test_resources.actions import do_raise, do_return
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsSingleDirDependentValue),
        unittest.makeSuite(TestEqualsMultiDirDependentValue),
    ])


class TestEqualsSingleDirDependentValue(unittest.TestCase):
    def test_pass(self):
        cases = [
            ASingleDirDependentValue(resolving_dependency=None,
                                     value_when_no_dir_dependencies=do_return('value'),
                                     value_pre_sds=do_return('value')),
            ASingleDirDependentValue(resolving_dependency=DirectoryStructurePartition.HOME,
                                     value_pre_sds=do_return('value pre sds')),
            ASingleDirDependentValue(resolving_dependency=DirectoryStructurePartition.NON_HOME,
                                     value_post_sds=do_return('value post sds'))
        ]
        for value in cases:
            with self.subTest(value=str(value)):
                assertion = sut.matches_single_dir_dependent_value(value)
                assertion.apply_without_message(self, value)

    def test_fail__has_dir_dependency(self):
        self._assert_not_equal(
            ASingleDirDependentValue(resolving_dependency=DirectoryStructurePartition.HOME),
            ASingleDirDependentValue(resolving_dependency=None),
        )

    def test_fail__exists_pre_sds(self):
        self._assert_not_equal(
            ASingleDirDependentValue(resolving_dependency=DirectoryStructurePartition.NON_HOME),
            ASingleDirDependentValue(resolving_dependency=DirectoryStructurePartition.HOME),
        )

    def test_fail__value_when_no_dir_dependencies(self):
        self._assert_not_equal(
            ASingleDirDependentValue(resolving_dependency=None,
                                     value_when_no_dir_dependencies=do_return('expected')),
            ASingleDirDependentValue(resolving_dependency=None,
                                     value_when_no_dir_dependencies=do_return('actual')),
        )

    def test_fail__value_pre_sds(self):
        self._assert_not_equal(
            ASingleDirDependentValue(resolving_dependency=DirectoryStructurePartition.HOME,
                                     value_pre_sds=do_return('expected')),
            ASingleDirDependentValue(resolving_dependency=DirectoryStructurePartition.HOME,
                                     value_pre_sds=do_return('actual')),
        )

    def test_fail__value_post_sds(self):
        self._assert_not_equal(
            ASingleDirDependentValue(resolving_dependency=DirectoryStructurePartition.NON_HOME,
                                     value_post_sds=do_return('expected')),
            ASingleDirDependentValue(resolving_dependency=DirectoryStructurePartition.NON_HOME,
                                     value_post_sds=do_return('actual')),
        )

    @staticmethod
    def _assert_not_equal(expected: sut.SingleDirDependentValue,
                          actual: sut.SingleDirDependentValue):
        assertion = sut.matches_single_dir_dependent_value(expected)
        assert_that_assertion_fails(assertion, actual)


class TestEqualsMultiDirDependentValue(unittest.TestCase):
    def test_pass(self):
        cases = [
            AMultiDirDependentValue(resolving_dependencies=set(),
                                    get_value_when_no_dir_dependencies=do_return('value when no dep'),
                                    get_value_of_any_dependency=do_return('value')),
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.HOME},
                                    get_value_of_any_dependency=do_return('value_of_any_dependency')),
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.NON_HOME},
                                    get_value_of_any_dependency=do_return('value_of_any_dependency'))
        ]
        for value in cases:
            with self.subTest(value=str(value)):
                assertion = sut.matches_multi_dir_dependent_value(value)
                assertion.apply_without_message(self, value)

    def test_fail__has_dir_dependency(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.HOME}),
            AMultiDirDependentValue(resolving_dependencies=set()),
        )

    def test_fail__exists_pre_sds(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.NON_HOME}),
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.HOME}),
        )

    def test_fail__exists_post_sds(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.HOME}),
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.NON_HOME}),
        )

    def test_fail__value_when_no_dir_dependencies(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies=set(),
                                    get_value_when_no_dir_dependencies=do_return('expected')),
            AMultiDirDependentValue(resolving_dependencies=set(),
                                    get_value_when_no_dir_dependencies=do_return('actual')),
        )

    def test_fail__value_pre_sds(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.HOME},
                                    get_value_of_any_dependency=do_return('expected')),
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.HOME},
                                    get_value_of_any_dependency=do_return('actual')),
        )

    def test_fail__value_post_sds(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.NON_HOME},
                                    get_value_of_any_dependency=do_return('expected')),
            AMultiDirDependentValue(resolving_dependencies={DirectoryStructurePartition.NON_HOME},
                                    get_value_of_any_dependency=do_return('actual')),
        )

    @staticmethod
    def _assert_not_equal(expected: sut.MultiDirDependentValue,
                          actual: sut.MultiDirDependentValue):
        assertion = sut.matches_multi_dir_dependent_value(expected)
        assert_that_assertion_fails(assertion, actual)


class _ShouldNotBeInvokedTestException(Exception):
    pass


class ASingleDirDependentValue(sut.SingleDirDependentValue):
    def __init__(self,
                 resolving_dependency: Optional[DirectoryStructurePartition],
                 value_when_no_dir_dependencies=do_raise(_ShouldNotBeInvokedTestException()),
                 value_pre_sds=do_raise(_ShouldNotBeInvokedTestException()),
                 value_post_sds=do_raise(_ShouldNotBeInvokedTestException()),
                 ):
        self._resolving_dependency = resolving_dependency
        self._value_when_no_dir_dependencies = value_when_no_dir_dependencies
        self._value_pre_sds = value_pre_sds
        self._value_post_sds = value_post_sds

    def resolving_dependency(self) -> Optional[DirectoryStructurePartition]:
        return self._resolving_dependency

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        if self._resolving_dependency is None:
            return set()
        else:
            return {self._resolving_dependency}

    def has_dir_dependency(self) -> bool:
        return self._resolving_dependency is not None

    def exists_pre_sds(self) -> bool:
        return self._resolving_dependency is None or self._resolving_dependency == DirectoryStructurePartition.HOME

    def value_when_no_dir_dependencies(self):
        return self._value_when_no_dir_dependencies()

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        return self._value_pre_sds(hds)

    def value_post_sds(self, sds: SandboxDirectoryStructure):
        return self._value_post_sds(sds)

    def __str__(self):
        return '{}(resolving_dependency={})'.format(
            type(self),
            self._resolving_dependency)


class MultiDirDependentValueTestImpl(Generic[RESOLVED_TYPE], sut.MultiDirDependentValue[RESOLVED_TYPE]):
    def __init__(self,
                 resolving_dependencies: Set[DirectoryStructurePartition],
                 value_when_no_dir_dependencies: RESOLVED_TYPE,
                 get_value_when_no_dir_dependencies: Callable[[], RESOLVED_TYPE]=None,
                 get_value_of_any_dependency: Callable[[HomeAndSds], RESOLVED_TYPE] = None,
                 ):
        self._resolving_dependencies = resolving_dependencies
        self._value_when_no_dir_dependencies = value_when_no_dir_dependencies
        self._get_value_when_no_dir_dependencies = get_value_when_no_dir_dependencies
        self._get_value_of_any_dependency = get_value_of_any_dependency

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._resolving_dependencies

    def dir_dependencies(self) -> DirDependencies:
        return dir_dependency_of_resolving_dependencies(self._resolving_dependencies)

    def has_dir_dependency(self) -> bool:
        return bool(self._resolving_dependencies)

    def exists_pre_sds(self) -> bool:
        return DirectoryStructurePartition.NON_HOME not in self._resolving_dependencies

    def value_when_no_dir_dependencies(self):
        if self._get_value_when_no_dir_dependencies is not None:
            return self._get_value_when_no_dir_dependencies()
        else:
            return self._value_when_no_dir_dependencies

    def value_of_any_dependency(self, home_and_sds: HomeAndSds):
        if self._get_value_of_any_dependency is None:
            return self.value_when_no_dir_dependencies()
        else:
            return self._get_value_of_any_dependency(home_and_sds)

    def __str__(self):
        return '{}(has_dir_dependency={has_dir_dependency}, exists_pre_sds={exists_pre_sds})'.format(
            type(self),
            has_dir_dependency=self.has_dir_dependency,
            exists_pre_sds=self.exists_pre_sds,
        )


class AMultiDirDependentValue(MultiDirDependentValueTestImpl[None]):
    def __init__(self,
                 resolving_dependencies: Set[DirectoryStructurePartition],
                 get_value_when_no_dir_dependencies=do_raise(_ShouldNotBeInvokedTestException()),
                 get_value_of_any_dependency=do_raise(_ShouldNotBeInvokedTestException()),
                 ):
        super().__init__(resolving_dependencies,
                         None,
                         get_value_when_no_dir_dependencies,
                         get_value_of_any_dependency)
