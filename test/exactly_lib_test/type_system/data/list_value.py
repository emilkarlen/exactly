import unittest

from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.data import concrete_string_values as sv, file_refs, list_value as sut
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsNothing
from exactly_lib.type_system.data.concrete_string_values import string_value_of_single_string
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    matches_multi_dir_dependent_value
from exactly_lib_test.test_case_file_structure.test_resources_test.dir_dependent_value import AMultiDirDependentValue
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.name_and_value import NameAndValue


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestListValue)


class TestListValue(unittest.TestCase):
    def test_dependence_and_resolving(self):
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
                    get_value_when_no_dir_dependencies=do_return([]),
                    get_value_of_any_dependency=do_return([])),
            ),
            (
                'single string constant element',
                sut.ListValue([sv.string_value_of_single_string(string_fragment_1)]),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    get_value_when_no_dir_dependencies=do_return([string_fragment_1]),
                    get_value_of_any_dependency=do_return([string_fragment_1])),
            ),
            (
                'multiple string constant element',
                sut.ListValue([sv.string_value_of_single_string(string_fragment_1),
                               sv.string_value_of_single_string(string_fragment_2)]),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    get_value_when_no_dir_dependencies=do_return([string_fragment_1, string_fragment_2]),
                    get_value_of_any_dependency=do_return([string_fragment_1, string_fragment_2])),
            ),
            (
                'single dir dependent value/pre sds',
                sut.ListValue([single_element_with_dep_on_home]),
                AMultiDirDependentValue(
                    resolving_dependencies={DirectoryStructurePartition.HOME},
                    get_value_of_any_dependency=lambda h_s:
                    [single_element_with_dep_on_home.value_of_any_dependency(h_s)]),
            ),
            (
                'single dir dependent value/post sds',
                sut.ListValue([single_element_with_dep_on_sds]),
                AMultiDirDependentValue(
                    resolving_dependencies={DirectoryStructurePartition.NON_HOME},
                    get_value_of_any_dependency=lambda h_s:
                    [single_element_with_dep_on_sds.value_of_any_dependency(h_s)]),
            ),
            (
                'multiple dir dependent value/pre sds + post sds',
                sut.ListValue([single_element_with_dep_on_home,
                               single_element_with_dep_on_sds]),
                AMultiDirDependentValue(
                    resolving_dependencies={DirectoryStructurePartition.HOME,
                                            DirectoryStructurePartition.NON_HOME},
                    get_value_of_any_dependency=lambda h_s: [
                        single_element_with_dep_on_home.value_of_any_dependency(h_s),
                        single_element_with_dep_on_sds.value_of_any_dependency(h_s)]
                ),
            ),
        ]
        for test_case_name, expected, actual in cases:
            assertion = matches_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name):
                assertion.apply_without_message(self, actual)

    def test_description(self):
        # ARRANGE #

        s1 = 'string1'
        s2 = 'string2'

        cases = [
            NameAndValue('empty',
                         [],
                         ),
            NameAndValue('singleton element',
                         [s1],
                         ),
            NameAndValue('multiple elements',
                         [s1, s2],
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                elements = [
                    string_value_of_single_string(s)
                    for s in case.value
                ]
                list_value_fragment = sut.ListValue(elements)

                # ACT #

                actual = list_value_fragment.describer().render_sequence()

                # ASSERT #

                self.assertEqual(case.value, actual)
