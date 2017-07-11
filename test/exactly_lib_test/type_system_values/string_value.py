import pathlib
import unittest

from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.type_system_values import string_value as sut, concrete_string_values as csv, file_refs
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsNothing
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    equals_multi_dir_dependent_value
from exactly_lib_test.test_case_file_structure.test_resources_test.dir_dependent_value import AMultiDirDependentValue
from exactly_lib_test.test_resources.actions import do_return


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstantFragment),
        unittest.makeSuite(TestFileRefFragment),
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
    def test_pass(self):
        file_ref_rel_home = file_refs.of_rel_option(file_refs.RelOptionType.REL_HOME,
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
                        file_ref_rel_home.value_pre_sds(h_s.home_dir_path))),
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
                    value_when_no_dir_dependencies=do_return(file_ref_abs.value_when_no_dir_dependencies()),
                    value_of_any_dependency=lambda h_s: str(
                        file_ref_abs.value_when_no_dir_dependencies())),
            ),
        ]
        for test_case_name, expected, actual in cases:
            assertion = equals_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name,
                              expected=str(expected)):
                assertion.apply_without_message(self, actual)


class TestStringValue(unittest.TestCase):
    def test_pass(self):
        file_ref_rel_home = file_refs.of_rel_option(file_refs.RelOptionType.REL_HOME,
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
                sut.StringValue(tuple([csv.ConstantFragment('fragment')])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return('fragment'),
                    value_of_any_dependency=do_return('fragment')),
            ),
            (
                'multiple string constant fragment',
                sut.StringValue(tuple([csv.ConstantFragment('fragment1'),
                                       csv.ConstantFragment('_fragment2')])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    value_when_no_dir_dependencies=do_return('fragment1_fragment2'),
                    value_of_any_dependency=do_return('fragment1_fragment2')),
            ),
            (
                'multiple dir dependent value/pre sds',
                sut.StringValue(tuple([csv.FileRefFragment(file_ref_rel_home)])),
                AMultiDirDependentValue(
                    resolving_dependencies={ResolvingDependency.HOME},
                    value_of_any_dependency=lambda h_s: str(
                        file_ref_rel_home.value_pre_sds(h_s.home_dir_path))),
            ),
            (
                'multiple dir dependent value/post sds',
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
                        str(file_ref_rel_home.value_pre_sds(h_s.home_dir_path)) +
                        str(file_ref_rel_sds.value_post_sds(h_s.sds)))
                ),
            ),
        ]
        for test_case_name, expected, actual in cases:
            assertion = equals_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name,
                              expected=str(expected)):
                assertion.apply_without_message(self, actual)
