import unittest
from typing import Set, Callable, Optional, Any

from exactly_lib.test_case_file_structure.dir_dependent_value import Max1DependencyDdv, \
    MultiDependenciesDdv, DirDependencies
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib_test.test_case_file_structure.test_resources import dir_dep_value_assertions as sut
from exactly_lib_test.test_resources.actions import do_raise, do_return
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMatchesSingleDirDependentValue),
        unittest.makeSuite(TestMatchesMultiDirDependentValue),
    ])


class TestMatchesSingleDirDependentValue(unittest.TestCase):
    def test_pass(self):
        resolved_value = 'resolved value'
        cases = [
            single_dir_dep_val_without_dependencies(resolved_value),
            single_dir_dep_val_with_dep_on_hds(do_return(resolved_value)),
            single_dir_dep_val_with_dep_on_sds(do_return(resolved_value)),
        ]
        for value in cases:
            with self.subTest(value=str(value)):
                assertion = sut.matches_single_dir_dependent_value(value.resolving_dependency(),
                                                                   lambda tcds: asrt.equals(resolved_value))
                assertion.apply_without_message(self, value)

    def test_fail__resolving_dependency(self):
        cases = [
            NEA('expects no dependencies',
                expected=None,
                actual=single_dir_dep_val_with_dep_on_hds(do_return('resolved_value'))
                ),
            NEA('expects dependencies',
                expected=DirectoryStructurePartition.HDS,
                actual=single_dir_dep_val_without_dependencies('resolved_value')
                ),
            NEA('expects correct dependency',
                expected=DirectoryStructurePartition.HDS,
                actual=single_dir_dep_val_with_dep_on_sds(do_return('resolved value'))
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                self._assert_not_matches(case.actual,
                                         case.expected,
                                         asrt.anything_goes(),
                                         )

    def test_fail__resolved_value(self):
        resolved_value = 'resolved value'

        self._assert_not_matches(
            single_dir_dep_val_without_dependencies(resolved_value),
            None,
            asrt.not_(asrt.equals(resolved_value))
        )

    @staticmethod
    def _assert_not_matches(actual: Max1DependencyDdv,
                            resolving_dependency: Optional[DirectoryStructurePartition],
                            resolved_value: ValueAssertion,
                            ):
        assertion = sut.matches_single_dir_dependent_value(resolving_dependency,
                                                           lambda tcds: resolved_value)
        assert_that_assertion_fails(assertion, actual)


class TestMatchesMultiDirDependentValue(unittest.TestCase):
    def test_pass(self):
        resolved_value = 'the resolved value'
        cases = [
            NameAndValue(
                'no dep',
                multi_dir_dep_val_without_dependencies(resolved_value)
            ),
            NameAndValue(
                str({DirectoryStructurePartition.HDS}),
                multi_dir_dep_val_with_dependencies({DirectoryStructurePartition.HDS},
                                                    get_value_of_any_dependency=do_return(resolved_value)),
            ),
            NameAndValue(
                str({DirectoryStructurePartition.NON_HDS}),
                multi_dir_dep_val_with_dependencies({DirectoryStructurePartition.NON_HDS},
                                                    get_value_of_any_dependency=do_return(resolved_value)),
            ),
            NameAndValue(
                str({DirectoryStructurePartition.HDS, DirectoryStructurePartition.NON_HDS}),
                multi_dir_dep_val_with_dependencies({DirectoryStructurePartition.HDS,
                                                     DirectoryStructurePartition.NON_HDS},
                                                    get_value_of_any_dependency=do_return(resolved_value)),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                assertion = sut.matches_multi_dir_dependent_value(case.value.dir_dependencies(),
                                                                  lambda tcds: asrt.equals(resolved_value))
                assertion.apply_without_message(self, case.value)

    def test_fail__dependency(self):
        resolved_value = 'the resolved value'
        cases = [
            NEA('invalid dep/none - NON_HDS',
                DirDependencies.HDS,
                multi_dir_dep_val_without_dependencies(resolved_value)
                ),
            NEA('invalid dep/HOME - NON_HDS',
                DirDependencies.HDS,
                multi_dir_dep_val_with_dependencies({DirectoryStructurePartition.NON_HDS},
                                                    do_return(resolved_value))
                ),
            NEA('invalid dep/HOME - HOME+NON_HDS',
                DirDependencies.HDS,
                multi_dir_dep_val_with_dependencies({DirectoryStructurePartition.HDS,
                                                     DirectoryStructurePartition.NON_HDS},
                                                    do_return(resolved_value))
                ),
            NEA('invalid dep/SDS - HOME',
                DirDependencies.SDS,
                multi_dir_dep_val_with_dependencies({DirectoryStructurePartition.HDS},
                                                    do_return(resolved_value))
                ),
            NEA('invalid dep/TCDS - NON_HDS',
                DirDependencies.TCDS,
                multi_dir_dep_val_with_dependencies({DirectoryStructurePartition.NON_HDS},
                                                    do_return(resolved_value))
                ),
            NEA('invalid dep/TCDS - {}',
                DirDependencies.TCDS,
                multi_dir_dep_val_with_dependencies(set(),
                                                    do_return(resolved_value))
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                self._assert_not_matches(
                    case.actual,
                    case.expected,
                    lambda tcds: asrt.anything_goes()
                )

    @staticmethod
    def _assert_not_matches(actual: MultiDependenciesDdv,
                            dir_dependencies: DirDependencies,
                            resolved_value: Callable[[Tcds], ValueAssertion[Any]]
                            ):
        assertion = sut.matches_multi_dir_dependent_value(dir_dependencies,
                                                          resolved_value)
        assert_that_assertion_fails(assertion, actual)


class _ShouldNotBeInvokedTestException(Exception):
    pass


class AMax1DependencyDdv(Max1DependencyDdv[Any]):
    def __init__(self,
                 resolving_dependency: Optional[DirectoryStructurePartition],
                 value_when_no_dir_dependencies: Callable[[], Any] = do_raise(_ShouldNotBeInvokedTestException()),
                 value_pre_sds: Callable[[HomeDirectoryStructure], Any] = do_raise(_ShouldNotBeInvokedTestException()),
                 value_post_sds: Callable[[SandboxDirectoryStructure], Any] =
                 do_raise(_ShouldNotBeInvokedTestException()),
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

    def value_when_no_dir_dependencies(self) -> Any:
        return self._value_when_no_dir_dependencies()

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> Any:
        return self._value_pre_sds(hds)

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> Any:
        return self._value_post_sds(sds)


def single_dir_dep_val_without_dependencies(resolved_value,
                                            ) -> Max1DependencyDdv:
    def when_no_dependencies():
        return resolved_value

    return AMax1DependencyDdv(None,
                              value_when_no_dir_dependencies=when_no_dependencies,
                              value_pre_sds=lambda hds: resolved_value,
                              value_post_sds=lambda sds: resolved_value)


def single_dir_dep_val_with_dep_on_hds(resolve_pre_sds: Callable[[HomeDirectoryStructure], Any],
                                       ) -> Max1DependencyDdv:
    return AMax1DependencyDdv(DirectoryStructurePartition.HDS,
                              value_pre_sds=resolve_pre_sds)


def single_dir_dep_val_with_dep_on_sds(resolve_post_sds: Callable[[SandboxDirectoryStructure], Any],
                                       ) -> Max1DependencyDdv:
    return AMax1DependencyDdv(DirectoryStructurePartition.NON_HDS,
                              value_post_sds=resolve_post_sds)


class AMultiDependenciesDdv(MultiDependenciesDdv[Any]):
    def __init__(self,
                 resolving_dependencies: Set[DirectoryStructurePartition],

                 get_value_when_no_dir_dependencies: Callable[[], Any] =
                 do_raise(_ShouldNotBeInvokedTestException()),

                 get_value_of_any_dependency: Callable[[Tcds], Any] =
                 do_raise(_ShouldNotBeInvokedTestException()),
                 ):
        self._resolving_dependencies = resolving_dependencies
        self._get_value_when_no_dir_dependencies = get_value_when_no_dir_dependencies
        self._get_value_of_any_dependency = get_value_of_any_dependency

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._resolving_dependencies

    def value_when_no_dir_dependencies(self):
        return self._get_value_when_no_dir_dependencies()

    def value_of_any_dependency(self, tcds: Tcds):
        return self._get_value_of_any_dependency(tcds)


def multi_dir_dep_val_without_dependencies(resolved_value,
                                           ) -> MultiDependenciesDdv:
    def when_no_dependencies():
        return resolved_value

    return AMultiDependenciesDdv(set(),
                                 get_value_when_no_dir_dependencies=when_no_dependencies,
                                 get_value_of_any_dependency=lambda tcds: resolved_value)


def multi_dir_dep_val_with_dependencies(resolving_dependencies: Set[DirectoryStructurePartition],
                                        get_value_of_any_dependency: Callable[[Tcds], Any],
                                        ) -> MultiDependenciesDdv:
    return AMultiDependenciesDdv(resolving_dependencies,
                                 get_value_of_any_dependency=get_value_of_any_dependency)
