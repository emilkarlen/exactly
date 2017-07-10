import unittest

from exactly_lib.symbol import concrete_string_values as csv
from exactly_lib.symbol import string_value as sut
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsNothing
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib_test.test_case_file_structure.test_resources.dir_dependent_value import \
    equals_multi_dir_dependent_value
from exactly_lib_test.test_case_file_structure.test_resources_test.dir_dependent_value import AMultiDirDependentValue
from exactly_lib_test.test_resources.actions import do_return


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDirDependency)
    ])


class TestDirDependency(unittest.TestCase):
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
