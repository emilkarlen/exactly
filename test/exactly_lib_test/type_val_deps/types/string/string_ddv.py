import pathlib
import unittest

from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_part_ddvs import PathPartDdvAsNothing
from exactly_lib.type_val_deps.types.string import string_ddv as sut, strings_ddvs as strings
from exactly_lib.type_val_deps.types.string.strings_ddvs import string_ddv_of_single_string, \
    string_ddv_of_single_path
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.type_val_deps.dep_variants.test_resources.dir_dependent_value import \
    matches_multi_dir_dependent_value
from exactly_lib_test.type_val_deps.dep_variants.test_resources_test.dir_dependent_value import AMultiDirDependentValue


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestConstantFragment),
        unittest.makeSuite(TestPathFragment),
        unittest.makeSuite(TestListFragment),
        unittest.makeSuite(TestStringValue),
        unittest.makeSuite(TestStringValueFragment),
        unittest.makeSuite(TestTransformedFragment),
    ])


class TestConstantFragment(unittest.TestCase):
    def test_dir_dependence(self):
        cases = [
            NEA(
                'single string constant fragment',
                expected=AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    get_value_when_no_dir_dependencies=do_return('fragment'),
                    get_value_of_any_dependency=do_return('fragment')),
                actual=strings.ConstantFragmentDdv('fragment'),
            ),
        ]
        for case in cases:
            assertion = matches_multi_dir_dependent_value(case.expected)
            with self.subTest(name=case.name,
                              expected=str(case.expected)):
                assertion.apply_without_message(self, case.actual)

    def test_description(self):
        # ARRANGE #
        fragment_string = 'fragment string'
        fragment = strings.ConstantFragmentDdv(fragment_string)

        # ACT #

        actual = fragment.describer().render()

        # ASSERT #

        self.assertEqual(fragment_string, actual)


class TestTransformedFragment(unittest.TestCase):
    def test(self):
        cases = [
            (
                'single string constant fragment',
                strings.TransformedStringFragmentDdv(strings.ConstantFragmentDdv('fragment'),
                                                     str.upper),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    get_value_when_no_dir_dependencies=do_return('FRAGMENT'),
                    get_value_of_any_dependency=do_return('FRAGMENT')),
            ),
        ]
        for test_case_name, actual, expected in cases:
            assertion = matches_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name,
                              expected=str(expected)):
                assertion.apply_without_message(self, actual)

    def test_description(self):
        # ARRANGE #
        transformed_string = 'the string'
        expected = transformed_string.upper()

        fragment = strings.TransformedStringFragmentDdv(strings.ConstantFragmentDdv(transformed_string),
                                                        str.upper)

        # ACT #

        actual = fragment.describer().render()

        # ASSERT #

        self.assertEqual(expected, actual)


class TestPathFragment(unittest.TestCase):
    def test(self):
        path_rel_home = path_ddvs.of_rel_option(path_ddvs.RelOptionType.REL_HDS_CASE,
                                                PathPartDdvAsNothing())
        path_rel_sds = path_ddvs.of_rel_option(path_ddvs.RelOptionType.REL_ACT,
                                               PathPartDdvAsNothing())
        path_abs = path_ddvs.absolute_file_name(str(pathlib.Path().resolve()))
        cases = [
            (
                'dependency on ' + str(DirectoryStructurePartition.HDS),
                strings.PathFragmentDdv(path_rel_home),
                AMultiDirDependentValue(
                    resolving_dependencies={DirectoryStructurePartition.HDS},
                    get_value_of_any_dependency=lambda h_s: str(
                        path_rel_home.value_pre_sds(h_s.hds))),
            ),
            (
                'dependency on ' + str(DirectoryStructurePartition.NON_HDS),
                strings.PathFragmentDdv(path_rel_sds),
                AMultiDirDependentValue(
                    resolving_dependencies={DirectoryStructurePartition.NON_HDS},
                    get_value_of_any_dependency=lambda h_s: str(
                        path_rel_sds.value_post_sds(h_s.sds))),
            ),
            (
                'no dependency',
                strings.PathFragmentDdv(path_abs),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    get_value_when_no_dir_dependencies=do_return(str(path_abs.value_when_no_dir_dependencies())),
                    get_value_of_any_dependency=lambda h_s: str(
                        path_abs.value_when_no_dir_dependencies())),
            ),
        ]
        for test_case_name, expected, actual in cases:
            assertion = matches_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name,
                              expected=str(expected)):
                assertion.apply_without_message(self, actual)

    def test_description(self):
        # ARRANGE #
        path_rel_home = path_ddvs.of_rel_option(path_ddvs.RelOptionType.REL_HDS_CASE,
                                                PathPartDdvAsNothing())
        path_rel_sds = path_ddvs.of_rel_option(path_ddvs.RelOptionType.REL_ACT,
                                               PathPartDdvAsNothing())
        path_abs = path_ddvs.absolute_file_name(str(pathlib.Path().resolve()))
        cases = [
            NameAndValue('rel-hds',
                         path_rel_home
                         ),
            NameAndValue('rel-sds',
                         path_rel_sds
                         ),
            NameAndValue('absolute',
                         path_abs
                         ),
        ]

        for case in cases:
            with self.subTest(case.name):
                fragment = strings.PathFragmentDdv(case.value)

                # ACT #

                actual = fragment.describer().render()

                # ASSERT #

                expected = case.value.describer().value.render()

                self.assertEqual(expected, actual)


class TestListFragment(unittest.TestCase):
    def test(self):
        string_of_path_rel_home = string_ddv_of_single_path(
            path_ddvs.of_rel_option(path_ddvs.RelOptionType.REL_HDS_CASE,
                                    PathPartDdvAsNothing()))
        string_1 = 'string value 1'
        string_2 = 'string value 2'
        cases = [
            (
                'single string constant element',
                strings.ListFragmentDdv(strings.ListDdv([string_ddv_of_single_string(string_1)])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    get_value_when_no_dir_dependencies=do_return(string_1),
                    get_value_of_any_dependency=do_return(string_1)),
            ),
            (
                'multiple string constant element',
                strings.ListFragmentDdv(strings.ListDdv([string_ddv_of_single_string(string_1),
                                                         string_ddv_of_single_string(string_2)])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    get_value_when_no_dir_dependencies=do_return(string_1 + ' ' + string_2),
                    get_value_of_any_dependency=do_return(string_1 + ' ' + string_2)),
            ),
            (
                'dependency on ' + str(DirectoryStructurePartition.HDS),
                strings.ListFragmentDdv(strings.ListDdv([string_of_path_rel_home])),
                AMultiDirDependentValue(
                    resolving_dependencies={DirectoryStructurePartition.HDS},
                    get_value_of_any_dependency=lambda h_s: str(
                        string_of_path_rel_home.value_of_any_dependency(h_s))),
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
                expected = ' '.join(case.value)
                elements = [
                    string_ddv_of_single_string(s)
                    for s in case.value
                ]
                list_fragment = strings.ListFragmentDdv(strings.ListDdv(elements))

                # ACT #

                actual = list_fragment.describer().render()

                # ASSERT #

                self.assertEqual(expected, actual)


class TestStringValue(unittest.TestCase):
    def test(self):
        string_fragment_1 = 'string fragment 1'
        string_fragment_2 = 'string fragment 2'
        path_rel_home = path_ddvs.of_rel_option(path_ddvs.RelOptionType.REL_HDS_CASE,
                                                PathPartDdvAsNothing())
        path_rel_sds = path_ddvs.of_rel_option(path_ddvs.RelOptionType.REL_ACT,
                                               PathPartDdvAsNothing())
        cases = [
            (
                'no fragments',
                sut.StringDdv(tuple([])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    get_value_when_no_dir_dependencies=do_return(''),
                    get_value_of_any_dependency=do_return('')),
            ),
            (
                'single string constant fragment',
                sut.StringDdv(tuple([strings.ConstantFragmentDdv(string_fragment_1)])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    get_value_when_no_dir_dependencies=do_return(string_fragment_1),
                    get_value_of_any_dependency=do_return(string_fragment_1)),
            ),
            (
                'multiple string constant fragment',
                sut.StringDdv(tuple([strings.ConstantFragmentDdv(string_fragment_1),
                                     strings.ConstantFragmentDdv(string_fragment_2)])),
                AMultiDirDependentValue(
                    resolving_dependencies=set(),
                    get_value_when_no_dir_dependencies=do_return(string_fragment_1 + string_fragment_2),
                    get_value_of_any_dependency=do_return(string_fragment_1 + string_fragment_2)),
            ),
            (
                'single dir dependent value/pre sds',
                sut.StringDdv(tuple([strings.PathFragmentDdv(path_rel_home)])),
                AMultiDirDependentValue(
                    resolving_dependencies={DirectoryStructurePartition.HDS},
                    get_value_of_any_dependency=lambda h_s: str(
                        path_rel_home.value_pre_sds(h_s.hds))),
            ),
            (
                'single dir dependent value/post sds',
                sut.StringDdv(tuple([strings.PathFragmentDdv(path_rel_sds)])),
                AMultiDirDependentValue(
                    resolving_dependencies={DirectoryStructurePartition.NON_HDS},
                    get_value_of_any_dependency=lambda h_s: str(
                        path_rel_sds.value_post_sds(h_s.sds))),
            ),
            (
                'multiple dir dependent value/pre sds + post sds',
                sut.StringDdv(tuple([strings.PathFragmentDdv(path_rel_home),
                                     strings.PathFragmentDdv(path_rel_sds)])),
                AMultiDirDependentValue(
                    resolving_dependencies={DirectoryStructurePartition.HDS,
                                            DirectoryStructurePartition.NON_HDS},
                    get_value_of_any_dependency=lambda h_s: (
                            str(path_rel_home.value_pre_sds(h_s.hds)) +
                            str(path_rel_sds.value_post_sds(h_s.sds)))
                ),
            ),
        ]
        for test_case_name, expected, actual in cases:
            assertion = matches_multi_dir_dependent_value(expected)
            with self.subTest(name=test_case_name,
                              expected=str(expected)):
                assertion.apply_without_message(self, actual)

    def test_description(self):
        # ARRANGE #

        s1 = 'string1'
        s2 = 'string2'

        cases = [
            NameAndValue('empty',
                         [],
                         ),
            NameAndValue('singleton fragment',
                         [s1],
                         ),
            NameAndValue('multiple fragments',
                         [s1, s2],
                         ),
        ]
        for case in cases:
            with self.subTest(case.name):
                expected = ''.join(case.value)
                fragments = [
                    strings.ConstantFragmentDdv(s)
                    for s in case.value
                ]
                string = strings.StringDdv(fragments)

                # ACT #

                actual = string.describer().render()

                # ASSERT #

                self.assertEqual(expected, actual)


class TestStringValueFragment(unittest.TestCase):
    def test_description(self):
        # ARRANGE #
        expected = 'the string'

        string_value_fragment = strings.StringDdvFragmentDdv(string_ddv_of_single_string(expected))

        # ACT #

        actual = string_value_fragment.describer().render()

        # ASSERT #

        self.assertEqual(expected, actual)
