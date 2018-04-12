import unittest
from typing import TypeVar, Callable, Set, Optional, Generic

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue, SingleDirDependentValue, \
    MultiDirDependentValue, DirDependencies, resolving_dependencies_from_dir_dependencies
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt

T = TypeVar('T')


def matches_dir_dependent_value(resolving_dependencies: asrt.ValueAssertion[Set[DirectoryStructurePartition]],
                                resolved_value: Callable[[HomeAndSds], asrt.ValueAssertion[T]]
                                ) -> asrt.ValueAssertion[DirDependentValue[T]]:
    return ArbitraryDirDependentValueAssertion(resolving_dependencies,
                                               resolved_value)


def matches_single_dir_dependent_value(resolving_dependency: Optional[DirectoryStructurePartition],
                                       resolved_value: Callable[[HomeAndSds], asrt.ValueAssertion[T]]
                                       ) -> asrt.ValueAssertion[DirDependentValue[T]]:
    return SingleDirDependentValueAssertion(resolving_dependency,
                                            resolved_value)


def matches_multi_dir_dependent_value(dir_dependencies: DirDependencies,
                                      resolved_value: Callable[[HomeAndSds], asrt.ValueAssertion[T]]
                                      ) -> asrt.ValueAssertion[DirDependentValue[T]]:
    return MultiDirDependentValueAssertion(dir_dependencies,
                                           resolved_value)


class DirDependentValueAssertionBase(Generic[T], asrt.ValueAssertion[DirDependentValue[T]]):
    def __init__(self,
                 resolving_dependencies: asrt.ValueAssertion[Set[DirectoryStructurePartition]],
                 resolved_value: Callable[[HomeAndSds], asrt.ValueAssertion[T]],
                 ):
        self.resolving_dependencies = resolving_dependencies
        self.resolved_value = resolved_value

    def _check_sub_class_properties(self,
                                    put: unittest.TestCase,
                                    actual: DirDependentValue,
                                    tcds: HomeAndSds,
                                    message_builder: asrt.MessageBuilder):
        raise NotImplementedError('abstract method')

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        asrt.is_instance(DirDependentValue).apply(put, value, message_builder)
        assert isinstance(value, DirDependentValue)  # Type info for IDE

        self._check_resolving_dependencies(put, value, message_builder)

        tcds = fake_home_and_sds()

        self._check_sub_class_properties(put, value, tcds, message_builder)

        self._check_resolved_value(put, value, tcds, message_builder)

    def _check_resolving_dependencies(self,
                                      put: unittest.TestCase,
                                      actual: DirDependentValue,
                                      message_builder: asrt.MessageBuilder):
        self.resolving_dependencies.apply(put,
                                          actual.resolving_dependencies(),
                                          message_builder.for_sub_component('resolving_dependencies'))
        actual_resolving_dependencies = actual.resolving_dependencies()

        as_dir_dependency_assertion = asrt.equals(bool(actual_resolving_dependencies))
        as_dir_dependency_assertion.apply(put,
                                          actual.has_dir_dependency(),
                                          message_builder.for_sub_component('has_dir_dependency'))

        should_exist_pre_sds = (not actual_resolving_dependencies
                                or
                                actual_resolving_dependencies == {DirectoryStructurePartition.HOME})
        asrt.equals(should_exist_pre_sds).apply(put,
                                                actual.exists_pre_sds(),
                                                message_builder.for_sub_component('exists_pre_sds'))

    def _check_resolved_value(self,
                              put: unittest.TestCase,
                              actual: DirDependentValue,
                              tcds: HomeAndSds,
                              message_builder: asrt.MessageBuilder):
        assertion_on_resolved_value = self.resolved_value(tcds)

        if not actual.has_dir_dependency():
            actual_resolved_value = actual.value_when_no_dir_dependencies()
            assertion_on_resolved_value.apply(put,
                                              actual_resolved_value,
                                              message_builder.for_sub_component('resolved primitive value'))

        actual_resolved_value = actual.value_of_any_dependency(tcds)
        assertion_on_resolved_value.apply(put,
                                          actual_resolved_value,
                                          message_builder.for_sub_component('resolved primitive value'))


class ArbitraryDirDependentValueAssertion(DirDependentValueAssertionBase[T]):
    def __init__(self,
                 resolving_dependencies: asrt.ValueAssertion[Set[DirectoryStructurePartition]],
                 resolved_value: Callable[[HomeAndSds], asrt.ValueAssertion[T]],
                 ):
        super().__init__(resolving_dependencies, resolved_value)

    def _check_sub_class_properties(self,
                                    put: unittest.TestCase,
                                    actual: DirDependentValue,
                                    tcds: HomeAndSds,
                                    message_builder: asrt.MessageBuilder):
        pass


class SingleDirDependentValueAssertion(DirDependentValueAssertionBase[T]):
    def __init__(self,
                 resolving_dependency: Optional[DirectoryStructurePartition],
                 resolved_value: Callable[[HomeAndSds], asrt.ValueAssertion[T]],
                 ):
        resolving_dependencies = asrt.is_empty if resolving_dependency is None else asrt.equals({resolving_dependency})
        super().__init__(resolving_dependencies, resolved_value)
        self._resolving_dependency = resolving_dependency

    def _check_sub_class_properties(self,
                                    put: unittest.TestCase,
                                    actual: DirDependentValue,
                                    tcds: HomeAndSds,
                                    message_builder: asrt.MessageBuilder):
        put.assertIsInstance(actual,
                             SingleDirDependentValue,
                             message_builder.apply('class'))
        assert isinstance(actual, SingleDirDependentValue)  # Type info for IDE

        put.assertEqual(self._resolving_dependency,
                        actual.resolving_dependency(),
                        message_builder.apply('resolving_dependency'))

        assertion_on_resolved_value = self.resolved_value(tcds)

        if not self._resolving_dependency or self._resolving_dependency == DirectoryStructurePartition.HOME:
            resolved_value_post_sds = actual.value_pre_sds(tcds.hds)
            assertion_on_resolved_value.apply(put,
                                              resolved_value_post_sds,
                                              message_builder.for_sub_component('value_pre_sds'))

        if not self._resolving_dependency or self._resolving_dependency == DirectoryStructurePartition.NON_HOME:
            resolved_value_post_sds = actual.value_post_sds(tcds.sds)
            assertion_on_resolved_value.apply(put,
                                              resolved_value_post_sds,
                                              message_builder.for_sub_component('value_pre_sds'))


class MultiDirDependentValueAssertion(DirDependentValueAssertionBase[T]):
    def __init__(self,
                 dir_dependencies: DirDependencies,
                 resolved_value: Callable[[HomeAndSds], asrt.ValueAssertion[T]],
                 ):
        super().__init__(asrt.equals(resolving_dependencies_from_dir_dependencies(dir_dependencies)),
                         resolved_value)
        self._dir_dependencies = dir_dependencies

    def _check_sub_class_properties(self,
                                    put: unittest.TestCase,
                                    actual: DirDependentValue,
                                    tcds: HomeAndSds,
                                    message_builder: asrt.MessageBuilder):
        put.assertIsInstance(actual,
                             MultiDirDependentValue,
                             message_builder.apply('class'))
        assert isinstance(actual, MultiDirDependentValue)  # Type info for IDE

        actual_dir_dependencies = actual.dir_dependencies()
        asrt.equals(self._dir_dependencies).apply(put,
                                                  actual_dir_dependencies,
                                                  message_builder.for_sub_component('dir_dependencies'))
