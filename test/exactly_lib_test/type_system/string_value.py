import pathlib
import unittest

from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.type_system import string_value as sut, concrete_string_values as csv, file_refs
from exactly_lib.type_system.concrete_string_values import string_value_of_single_string, \
    string_value_of_single_file_ref
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsNothing
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    equals_multi_dir_dependent_value
from exactly_lib_test.test_case_file_structure.test_resources_test.dir_dependent_value import AMultiDirDependentValue
from exactly_lib_test.test_resources.actions import do_return


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstantFragment),
        unittest.makeSuite(TestFileRefFragment),
        unittest.makeSuite(TestListFragment),
        unittest.makeSuite(TestStringValue),
    ])


class TestConstantFragment(unittest.TestCase):
    def test(self):
        cases = [
            (
                'single string constant fragment',
                csv.ConstantFragment('fragment'),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return('fragment'),
                    value_of_any_dependency=do_return('fragment')),
            ),
        ]
        for test_case_name, expected, actual in cases:
            assertion = equals_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name,
                              expected=str(expected)):
                assertion.apply_without_message(self, actual)


class TestFileRefFragment(unittest.TestCase):
    def test(self):
        file_ref_rel_home = file_refs.of_rel_option(file_refs.RelOptionType.REL_HOME_CASE,
                                                    PathPartAsNothing())
        file_ref_rel_sds = file_refs.of_rel_option(file_refs.RelOptionType.REL_ACT,
                                                   PathPartAsNothing())
        file_ref_abs = file_refs.absolute_file_name(str(pathlib.Path().resolve()))
        cases = [
            (
                'dependency on ' + str(ResolvingDependency.HOME),
                csv.FileRefFragment(file_ref_rel_home),
                AMultiDirDependentValue(
                    resolving_dependencies={ResolvingDependency.HOME},
                    value_of_any_dependency=lambda h_s: str(
                        file_ref_rel_home.value_pre_sds(h_s.hds))),
            ),
            (
                'dependency on ' + str(ResolvingDependency.NON_HOME),
                csv.FileRefFragment(file_ref_rel_sds),
                AMultiDirDependentValue(
                    resolving_dependencies={ResolvingDependency.NON_HOME},
                    value_of_any_dependency=lambda h_s: str(
                        file_ref_rel_sds.value_post_sds(h_s.sds))),
            ),
            (
                'no dependency',
                csv.FileRefFragment(file_ref_abs),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return(str(file_ref_abs.value_when_no_dir_dependencies())),
                    value_of_any_dependency=lambda h_s: str(
                        file_ref_abs.value_when_no_dir_dependencies())),
            ),
        ]
        for test_case_name, expected, actual in cases:
            assertion = equals_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name,
                              expected=str(expected)):
                assertion.apply_without_message(self, actual)


class TestListFragment(unittest.TestCase):
    def test(self):
        string_of_file_ref_rel_home = string_value_of_single_file_ref(
            file_refs.of_rel_option(file_refs.RelOptionType.REL_HOME_CASE,
                                    PathPartAsNothing()))
        string_1 = 'string value 1'
        string_2 = 'string value 2'
        cases = [
            (
                'single string constant element',
                csv.ListValueFragment(csv.ListValue([string_value_of_single_string(string_1)])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return(string_1),
                    value_of_any_dependency=do_return(string_1)),
            ),
            (
                'multiple string constant element',
                csv.ListValueFragment(csv.ListValue([string_value_of_single_string(string_1),
                                                     string_value_of_single_string(string_2)])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return(string_1 + ' ' + string_2),
                    value_of_any_dependency=do_return(string_1 + ' ' + string_2)),
            ),
            (
                'dependency on ' + str(ResolvingDependency.HOME),
                csv.ListValueFragment(csv.ListValue([string_of_file_ref_rel_home])),
                AMultiDirDependentValue(
                    resolving_dependencies={ResolvingDependency.HOME},
                    value_of_any_dependency=lambda h_s: str(
                        string_of_file_ref_rel_home.value_of_any_dependency(h_s))),
            ),
        ]
        for test_case_name, expected, actual in cases:
            assertion = equals_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name):
                assertion.apply_without_message(self, actual)


class TestStringValue(unittest.TestCase):
    def test(self):
        string_fragment_1 = 'string fragment 1'
        string_fragment_2 = 'string fragment 2'
        file_ref_rel_home = file_refs.of_rel_option(file_refs.RelOptionType.REL_HOME_CASE,
                                                    PathPartAsNothing())
        file_ref_rel_sds = file_refs.of_rel_option(file_refs.RelOptionType.REL_ACT,
                                                   PathPartAsNothing())
        cases = [
            (
                'no fragments',
                sut.StringValue(tuple([])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return(''),
                    value_of_any_dependency=do_return('')),
            ),
            (
                'single string constant fragment',
                sut.StringValue(tuple([csv.ConstantFragment(string_fragment_1)])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return(string_fragment_1),
                    value_of_any_dependency=do_return(string_fragment_1)),
            ),
            (
                'multiple string constant fragment',
                sut.StringValue(tuple([csv.ConstantFragment(string_fragment_1),
                                       csv.ConstantFragment(string_fragment_2)])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return(string_fragment_1 + string_fragment_2),
                    value_of_any_dependency=do_return(string_fragment_1 + string_fragment_2)),
            ),
            (
                'single dir dependent value/pre sds',
                sut.StringValue(tuple([csv.FileRefFragment(file_ref_rel_home)])),
                AMultiDirDependentValue(
                    resolving_dependencies={ResolvingDependency.HOME},
                    value_of_any_dependency=lambda h_s: str(
                        file_ref_rel_home.value_pre_sds(h_s.hds))),
            ),
            (
                'single dir dependent value/post sds',
                sut.StringValue(tuple([csv.FileRefFragment(file_ref_rel_sds)])),
                AMultiDirDependentValue(
                    resolving_dependencies={ResolvingDependency.NON_HOME},
                    value_of_any_dependency=lambda h_s: str(
                        file_ref_rel_sds.value_post_sds(h_s.sds))),
            ),
            (
                'multiple dir dependent value/pre sds + post sds',
                sut.StringValue(tuple([csv.FileRefFragment(file_ref_rel_home),
                                       csv.FileRefFragment(file_ref_rel_sds)])),
                AMultiDirDependentValue(
                    resolving_dependencies={ResolvingDependency.HOME,
                                            ResolvingDependency.NON_HOME},
                    value_of_any_dependency=lambda h_s: (
                        str(file_ref_rel_home.value_pre_sds(h_s.hds)) +
                        str(file_ref_rel_sds.value_post_sds(h_s.sds)))
                ),
            ),
        ]
        for test_case_name, expected, actual in cases:
            assertion = equals_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name,
                              expected=str(expected)):
                assertion.apply_without_message(self, actual)
