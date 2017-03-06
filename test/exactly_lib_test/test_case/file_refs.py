import unittest

from exactly_lib.test_case import file_refs as sut
from exactly_lib.test_case.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.value_definition import ValueReference
from exactly_lib.util.symbol_table import empty_symbol_table, singleton_symbol_table
from exactly_lib_test.test_case.test_resources import value_definition as vdtr
from exactly_lib_test.test_resources.execution.home_and_sds_check.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.execution.sds_check.sds_populator import act_dir_contents, tmp_user_dir_contents, \
    tmp_internal_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestRelHome))
    ret_val.addTest(unittest.makeSuite(TestRelCwd))
    ret_val.addTest(unittest.makeSuite(TestRelTmpUser))
    ret_val.addTest(unittest.makeSuite(TestRelTmpInternal))
    ret_val.addTest(unittest.makeSuite(TestRelValueDefinition))
    return ret_val


class TestRelHome(unittest.TestCase):
    def test_should_reference_no_value_definitions(self):
        file_reference = sut.rel_home('file.txt')
        self.assertTrue(len(file_reference.value_references()) == 0,
                        'File is expected to reference no variable definitions')

    def test_exists_pre_sds(self):
        file_reference = sut.rel_home('file.txt')
        self.assertTrue(file_reference.exists_pre_sds(empty_symbol_table()),
                        'File is expected to exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_home('file.txt')
        with home_and_sds_with_act_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assertTrue(file_reference.file_path_pre_sds(environment).exists())
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_home('file.txt')
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assertFalse(file_reference.file_path_pre_sds(environment).exists())
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())


class TestRelCwd(unittest.TestCase):
    def test_should_reference_no_value_definitions(self):
        file_reference = sut.rel_cwd('file.txt')
        self.assertTrue(len(file_reference.value_references()) == 0,
                        'File is expected to reference no variable definitions')

    def test_exists_pre_sds(self):
        file_reference = sut.rel_cwd('file.txt')
        self.assertFalse(file_reference.exists_pre_sds(empty_symbol_table()),
                         'File is expected to not exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_cwd('file.txt')
        with home_and_sds_with_act_as_curr_dir(
                sds_contents=act_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_cwd('file.txt')
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())


class TestRelTmpUser(unittest.TestCase):
    def test_should_reference_no_value_definitions(self):
        file_reference = sut.rel_tmp_user('file.txt')
        self.assertTrue(len(file_reference.value_references()) == 0,
                        'File is expected to reference no variable definitions')

    def test_exists_pre_sds(self):
        file_reference = sut.rel_tmp_user('file.txt')
        self.assertFalse(file_reference.exists_pre_sds(empty_symbol_table()),
                         'File is expected to not exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_tmp_user('file.txt')
        with home_and_sds_with_act_as_curr_dir(
                sds_contents=tmp_user_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, empty_symbol_table())
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_tmp_user('file.txt')
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, empty_symbol_table())
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())


class TestRelTmpInternal(unittest.TestCase):
    def test_should_reference_no_value_definitions(self):
        file_reference = sut.rel_tmp_internal('file.txt')
        self.assertTrue(len(file_reference.value_references()) == 0,
                        'File is expected to reference no variable definitions')

    def test_exists_pre_sds(self):
        file_reference = sut.rel_tmp_internal('file.txt')
        self.assertFalse(file_reference.exists_pre_sds(1),
                         'File is expected to not exist pre SDS')

    def test_existing_file(self):
        file_reference = sut.rel_tmp_internal('file.txt')
        with home_and_sds_with_act_as_curr_dir(
                sds_contents=tmp_internal_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file(self):
        file_reference = sut.rel_tmp_internal('file.txt')
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds)
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())


class TestRelValueDefinition(unittest.TestCase):
    def test_should_reference_exactly_one_value_definition(self):
        # ARRANGE #
        file_reference = sut.rel_value_definition('file.txt', 'value_definition_name')
        # ACT #
        actual = file_reference.value_references()
        # ASSERT #
        self.assertEqual(1, len(actual),
                         'There should be exactly one ValueReference')
        actual_vr = actual[0]
        self.assertIsInstance(actual_vr, ValueReference)
        assert isinstance(actual_vr, ValueReference)
        self.assertEqual('value_definition_name', actual_vr.name)

    def test_exists_pre_sds_for_value_that_exists_pre_sds(self):
        file_reference = sut.rel_value_definition('file.txt', 'value_definition_name')
        value_definitions = singleton_symbol_table(
            vdtr.entry('value_definition_name',
                       vdtr.file_ref_value(file_ref=sut.rel_home('file-name'))))
        self.assertTrue(file_reference.exists_pre_sds(value_definitions),
                        'File is expected to exist pre SDS')

    def test_exists_pre_sds_for_value_that_does_not_exist_pre_sds(self):
        file_reference = sut.rel_value_definition('file.txt', 'value_definition_name')
        value_definitions = singleton_symbol_table(
            vdtr.entry('value_definition_name',
                       vdtr.file_ref_value(file_ref=sut.rel_tmp_user('file-name'))))
        self.assertFalse(file_reference.exists_pre_sds(value_definitions),
                         'File is expected to not exist pre SDS')

    def test_existing_file__pre_sds(self):
        file_reference = sut.rel_value_definition('file.txt', 'rel_home_path_value')
        with home_and_sds_with_act_as_curr_dir(
                home_dir_contents=DirContents([empty_file('file.txt')])) as home_and_sds:
            value_definitions = singleton_symbol_table(
                vdtr.entry('rel_home_path_value',
                           vdtr.file_ref_value(file_ref=sut.rel_home('file.txt'))))
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, value_definitions)
            self.assertTrue(file_reference.file_path_pre_sds(environment).exists())
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_existing_file__post_sds(self):
        file_reference = sut.rel_value_definition('file.txt', 'rel_tmp_user_path_value')
        with home_and_sds_with_act_as_curr_dir(
                sds_contents=tmp_user_dir_contents(DirContents([empty_file('file.txt')]))) as home_and_sds:
            value_definitions = singleton_symbol_table(
                vdtr.entry('rel_tmp_user_path_value',
                           vdtr.file_ref_value(file_ref=sut.rel_tmp_user('file.txt'))))
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, value_definitions)
            self.assertTrue(file_reference.file_path_post_sds(environment).exists())
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file__pre_sds(self):
        file_reference = sut.rel_value_definition('file.txt', 'rel_home_path_value')
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            value_definitions = singleton_symbol_table(
                vdtr.entry('rel_home_path_value',
                           vdtr.file_ref_value(file_ref=sut.rel_home('file.txt'))))
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, value_definitions)
            self.assertFalse(file_reference.file_path_pre_sds(environment).exists())
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file__post_sds(self):
        file_reference = sut.rel_value_definition('file.txt', 'rel_tmp_user_path_value')
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            value_definitions = singleton_symbol_table(
                vdtr.entry('rel_tmp_user_path_value',
                           vdtr.file_ref_value(file_ref=sut.rel_tmp_user('file.txt'))))
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, value_definitions)
            self.assertFalse(file_reference.file_path_post_sds(environment).exists())
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
