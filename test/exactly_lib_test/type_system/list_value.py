import unittest

from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.type_system import concrete_string_values as sv
from exactly_lib.type_system import file_refs
from exactly_lib.type_system import list_value as sut
from exactly_lib.type_system.concrete_path_parts import PathPartAsNothing
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    equals_multi_dir_dependent_value
from exactly_lib_test.test_case_file_structure.test_resources_test.dir_dependent_value import AMultiDirDependentValue
from exactly_lib_test.test_resources.actions import do_return


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestListValue)


class TestListValue(unittest.TestCase):
    def test(self):
        string_fragment_1 = 'string fragment 1'
        string_fragment_2 = 'string fragment 2'
        file_ref_rel_home = file_refs.of_rel_option(file_refs.RelOptionType.REL_HOME_CASE,
                                                    PathPartAsNothing())
        file_ref_rel_sds = file_refs.of_rel_option(file_refs.RelOptionType.REL_ACT,
                                                   PathPartAsNothing())
        single_element_with_dep_on_home = sv.string_value_of_single_file_ref(file_ref_rel_home)
        single_element_with_dep_on_sds = sv.string_value_of_single_file_ref(file_ref_rel_sds)
        cases = [
            (
                'no elements',
                sut.ListValue([]),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return([]),
                    value_of_any_dependency=do_return([])),
            ),
            (
                'single string constant element',
                sut.ListValue([sv.string_value_of_single_string(string_fragment_1)]),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return([string_fragment_1]),
                    value_of_any_dependency=do_return([string_fragment_1])),
            ),
            (
                'multiple string constant element',
                sut.ListValue([sv.string_value_of_single_string(string_fragment_1),
                               sv.string_value_of_single_string(string_fragment_2)]),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return([string_fragment_1, string_fragment_2]),
                    value_of_any_dependency=do_return([string_fragment_1, string_fragment_2])),
            ),
            (
                'single dir dependent value/pre sds',
                sut.ListValue([single_element_with_dep_on_home]),
                AMultiDirDependentValue(
                    resolving_dependencies={ResolvingDependency.HOME},
                    value_of_any_dependency=lambda h_s:
                    [single_element_with_dep_on_home.value_of_any_dependency(h_s)]),
            ),
            (
                'single dir dependent value/post sds',
                sut.ListValue([single_element_with_dep_on_sds]),
                AMultiDirDependentValue(
                    resolving_dependencies={ResolvingDependency.NON_HOME},
                    value_of_any_dependency=lambda h_s:
                    [single_element_with_dep_on_sds.value_of_any_dependency(h_s)]),
            ),
            (
                'multiple dir dependent value/pre sds + post sds',
                sut.ListValue([single_element_with_dep_on_home,
                               single_element_with_dep_on_sds]),
                AMultiDirDependentValue(
                    resolving_dependencies={ResolvingDependency.HOME,
                                            ResolvingDependency.NON_HOME},
                    value_of_any_dependency=lambda h_s: [
                        single_element_with_dep_on_home.value_of_any_dependency(h_s),
                        single_element_with_dep_on_sds.value_of_any_dependency(h_s)]
                ),
            ),
        ]
        for test_case_name, expected, actual in cases:
            assertion = equals_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name):
                assertion.apply_without_message(self, actual)
