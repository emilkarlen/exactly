import pathlib
import unittest

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencies, \
    dir_dependency_of_resolving_dependencies
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_case_file_structure.test_resources import dir_dependent_value as sut
from exactly_lib_test.test_resources.actions import do_raise, do_return
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails


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
            ASingleDirDependentValue(resolving_dependency=ResolvingDependency.HOME,
                                     value_pre_sds=do_return('value pre sds')),
            ASingleDirDependentValue(resolving_dependency=ResolvingDependency.NON_HOME,
                                     value_post_sds=do_return('value post sds'))
        ]
        for value in cases:
            with self.subTest(value=str(value)):
                assertion = sut.equals_single_dir_dependent_value(value)
                assertion.apply_without_message(self, value)

    def test_fail__has_dir_dependency(self):
        self._assert_not_equal(
            ASingleDirDependentValue(resolving_dependency=ResolvingDependency.HOME),
            ASingleDirDependentValue(resolving_dependency=None),
        )

    def test_fail__exists_pre_sds(self):
        self._assert_not_equal(
            ASingleDirDependentValue(resolving_dependency=ResolvingDependency.NON_HOME),
            ASingleDirDependentValue(resolving_dependency=ResolvingDependency.HOME),
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
            ASingleDirDependentValue(resolving_dependency=ResolvingDependency.HOME,
                                     value_pre_sds=do_return('expected')),
            ASingleDirDependentValue(resolving_dependency=ResolvingDependency.HOME,
                                     value_pre_sds=do_return('actual')),
        )

    def test_fail__value_post_sds(self):
        self._assert_not_equal(
            ASingleDirDependentValue(resolving_dependency=ResolvingDependency.NON_HOME,
                                     value_post_sds=do_return('expected')),
            ASingleDirDependentValue(resolving_dependency=ResolvingDependency.NON_HOME,
                                     value_post_sds=do_return('actual')),
        )

    @staticmethod
    def _assert_not_equal(expected: sut.SingleDirDependentValue,
                          actual: sut.SingleDirDependentValue):
        assertion = sut.equals_single_dir_dependent_value(expected)
        assert_that_assertion_fails(assertion, actual)


class TestEqualsMultiDirDependentValue(unittest.TestCase):
    def test_pass(self):
        cases = [
            AMultiDirDependentValue(resolving_dependencies=set(),
                                    value_when_no_dir_dependencies=do_return('value when no dep'),
                                    value_pre_or_post_sds=do_return('value')),
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.HOME},
                                    value_pre_or_post_sds=do_return('value_pre_or_post_sds')),
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.NON_HOME},
                                    value_pre_or_post_sds=do_return('value_pre_or_post_sds'))
        ]
        for value in cases:
            with self.subTest(value=str(value)):
                assertion = sut.equals_multi_dir_dependent_value(value)
                assertion.apply_without_message(self, value)

    def test_fail__has_dir_dependency(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.HOME}),
            AMultiDirDependentValue(resolving_dependencies=set()),
        )

    def test_fail__exists_pre_sds(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.NON_HOME}),
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.HOME}),
        )

    def test_fail__exists_post_sds(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.HOME}),
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.NON_HOME}),
        )

    def test_fail__value_when_no_dir_dependencies(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies=set(),
                                    value_when_no_dir_dependencies=do_return('expected')),
            AMultiDirDependentValue(resolving_dependencies=set(),
                                    value_when_no_dir_dependencies=do_return('actual')),
        )

    def test_fail__value_pre_sds(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.HOME},
                                    value_pre_or_post_sds=do_return('expected')),
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.HOME},
                                    value_pre_or_post_sds=do_return('actual')),
        )

    def test_fail__value_post_sds(self):
        self._assert_not_equal(
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.NON_HOME},
                                    value_pre_or_post_sds=do_return('expected')),
            AMultiDirDependentValue(resolving_dependencies={ResolvingDependency.NON_HOME},
                                    value_pre_or_post_sds=do_return('actual')),
        )

    @staticmethod
    def _assert_not_equal(expected: sut.MultiDirDependentValue,
                          actual: sut.MultiDirDependentValue):
        assertion = sut.equals_multi_dir_dependent_value(expected)
        assert_that_assertion_fails(assertion, actual)


class _ShouldNotBeInvokedTestException(Exception):
    pass


class ASingleDirDependentValue(sut.SingleDirDependentValue):
    def __init__(self,
                 resolving_dependency: ResolvingDependency,
                 value_when_no_dir_dependencies=do_raise(_ShouldNotBeInvokedTestException()),
                 value_pre_sds=do_raise(_ShouldNotBeInvokedTestException()),
                 value_post_sds=do_raise(_ShouldNotBeInvokedTestException()),
                 ):
        self._resolving_dependency = resolving_dependency
        self._value_when_no_dir_dependencies = value_when_no_dir_dependencies
        self._value_pre_sds = value_pre_sds
        self._value_post_sds = value_post_sds

    def resolving_dependency(self) -> ResolvingDependency:
        return self._resolving_dependency

    def resolving_dependencies(self) -> set:
        if self._resolving_dependency is None:
            return set()
        else:
            return {self._resolving_dependency}

    def has_dir_dependency(self) -> bool:
        return self._resolving_dependency is not None

    def exists_pre_sds(self) -> bool:
        return self._resolving_dependency is None or self._resolving_dependency == ResolvingDependency.HOME

    def value_when_no_dir_dependencies(self):
        return self._value_when_no_dir_dependencies()

    def value_pre_sds(self, home_dir_path: pathlib.Path):
        return self._value_pre_sds(home_dir_path)

    def value_post_sds(self, sds: SandboxDirectoryStructure):
        return self._value_post_sds(sds)

    def __str__(self):
        return '{}(resolving_dependency={})'.format(
            type(self),
            self._resolving_dependency)


class AMultiDirDependentValue(sut.MultiDirDependentValue):
    def __init__(self,
                 resolving_dependencies: set,
                 value_when_no_dir_dependencies=do_raise(_ShouldNotBeInvokedTestException()),
                 value_pre_or_post_sds=do_raise(_ShouldNotBeInvokedTestException()),
                 ):
        self._resolving_dependencies = resolving_dependencies
        self._value_when_no_dir_dependencies = value_when_no_dir_dependencies
        self._value_pre_or_post_sds = value_pre_or_post_sds

    def resolving_dependencies(self) -> set:
        return self._resolving_dependencies

    def dir_dependency(self) -> DirDependencies:
        return dir_dependency_of_resolving_dependencies(self._resolving_dependencies)

    def has_dir_dependency(self) -> bool:
        return bool(self._resolving_dependencies)

    def exists_pre_sds(self) -> bool:
        return ResolvingDependency.NON_HOME not in self._resolving_dependencies

    def value_when_no_dir_dependencies(self):
        return self._value_when_no_dir_dependencies()

    def value_pre_or_post_sds(self, home_and_sds: HomeAndSds):
        return self._value_pre_or_post_sds(home_and_sds)

    def __str__(self):
        return '{}(has_dir_dependency={has_dir_dependency}, exists_pre_sds={exists_pre_sds})'.format(
            type(self),
            has_dir_dependency=self.has_dir_dependency,
            exists_pre_sds=self.exists_pre_sds,
        )
