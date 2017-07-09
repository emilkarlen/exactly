import pathlib
import unittest

from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib_test.test_case_file_structure.test_resources import dir_dependent_value as sut
from exactly_lib_test.test_resources.actions import do_raise, do_return
from exactly_lib_test.test_resources.value_assertions.assert_that_assertion_fails import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEquals)
    ])


class TestEquals(unittest.TestCase):
    def test_pass(self):
        cases = [
            _ADirDependentValue(has_dir_dependency=False,
                                exists_pre_sds=True,
                                value_when_no_dir_dependencies=do_return('value'),
                                value_pre_sds=do_return('value')),
            _ADirDependentValue(has_dir_dependency=True,
                                exists_pre_sds=True,
                                value_pre_sds=do_return('value pre sds')),
            _ADirDependentValue(has_dir_dependency=True,
                                exists_pre_sds=False,
                                value_post_sds=do_return('value post sds'))
        ]
        for value in cases:
            with self.subTest(value=str(value)):
                assertion = sut.equals_dir_dependent_value(value)
                assertion.apply_without_message(self, value)

    def test_fail__has_dir_dependency(self):
        _assert_not_equal(
            _ADirDependentValue(has_dir_dependency=True,
                                exists_pre_sds=True),
            _ADirDependentValue(has_dir_dependency=False,
                                exists_pre_sds=True),
        )

    def test_fail__exists_pre_sds(self):
        _assert_not_equal(
            _ADirDependentValue(has_dir_dependency=True,
                                exists_pre_sds=False),
            _ADirDependentValue(has_dir_dependency=True,
                                exists_pre_sds=True),
        )

    def test_fail__value_when_no_dir_dependencies(self):
        _assert_not_equal(
            _ADirDependentValue(has_dir_dependency=False,
                                exists_pre_sds=True,
                                value_when_no_dir_dependencies=do_return('expected')),
            _ADirDependentValue(has_dir_dependency=False,
                                exists_pre_sds=True,
                                value_when_no_dir_dependencies=do_return('actual')),
        )

    def test_fail__value_pre_sds(self):
        _assert_not_equal(
            _ADirDependentValue(has_dir_dependency=True,
                                exists_pre_sds=True,
                                value_pre_sds=do_return('expected')),
            _ADirDependentValue(has_dir_dependency=True,
                                exists_pre_sds=True,
                                value_pre_sds=do_return('actual')),
        )

    def test_fail__value_post_sds(self):
        _assert_not_equal(
            _ADirDependentValue(has_dir_dependency=True,
                                exists_pre_sds=False,
                                value_post_sds=do_return('expected')),
            _ADirDependentValue(has_dir_dependency=True,
                                exists_pre_sds=False,
                                value_post_sds=do_return('actual')),
        )


def _assert_not_equal(expected: sut.DirDependentValue,
                      actual: sut.DirDependentValue):
    assertion = sut.equals_dir_dependent_value(expected)
    assert_that_assertion_fails(assertion, actual)


class _TestException(Exception):
    pass


class _ADirDependentValue(sut.DirDependentValue):
    def __init__(self,
                 has_dir_dependency: bool,
                 exists_pre_sds: bool,
                 value_when_no_dir_dependencies=do_raise(_TestException()),
                 value_pre_sds=do_raise(_TestException()),
                 value_post_sds=do_raise(_TestException()),
                 ):
        self._has_dir_dependency = has_dir_dependency
        self._exists_pre_sds = exists_pre_sds
        self._value_when_no_dir_dependencies = value_when_no_dir_dependencies
        self._value_pre_sds = value_pre_sds
        self._value_post_sds = value_post_sds

    def has_dir_dependency(self) -> bool:
        return self._has_dir_dependency

    def exists_pre_sds(self) -> bool:
        return self._exists_pre_sds

    def value_when_no_dir_dependencies(self):
        return self._value_when_no_dir_dependencies()

    def value_pre_sds(self, home_dir_path: pathlib.Path):
        return self._value_pre_sds(home_dir_path)

    def value_post_sds(self, sds: SandboxDirectoryStructure):
        return self._value_post_sds(sds)

    def __str__(self):
        return '{}(has_dir_dependency={has_dir_dependency}, exists_pre_sds={exists_pre_sds})'.format(
            type(self),
            has_dir_dependency=self.has_dir_dependency,
            exists_pre_sds=self.exists_pre_sds,
        )
