import pathlib
import unittest

from exactly_lib.test_case_file_structure import file_refs as sut
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds, \
    PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.symbol_table import singleton_symbol_table
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.value_definition.file_ref_with_val_def import rel_value_definition
from exactly_lib.value_definition.value_structure import ValueReference
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import tmp_user_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, Dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources import value_definition_utils as v2
from exactly_lib_test.value_definition.test_resources import value_reference_assertions as vr_tr
from exactly_lib_test.value_definition.test_resources.concrete_restriction_assertion import \
    equals_file_ref_relativity_restriction


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestRelValueDefinition))
    return ret_val


class TestRelValueDefinition(unittest.TestCase):
    def test_should_reference_exactly_one_value_definition(self):
        # ARRANGE #
        expected_restriction = FileRefRelativityRestriction(
            PathRelativityVariants({RelOptionType.REL_ACT, RelOptionType.REL_HOME}, True))
        value_ref_of_path = ValueReference('value_definition_name',
                                           expected_restriction)
        file_reference = rel_value_definition(value_ref_of_path, PathPartAsFixedPath('file.txt'))
        # ACT #
        actual = file_reference.value_references_of_paths()
        # ASSERT #
        asrt.matches_sequence([
            vr_tr.equals_value_reference('value_definition_name',
                                         equals_file_ref_relativity_restriction(expected_restriction))
        ]).apply_with_message(self, actual, 'value_references_of_paths')

    def test_exists_pre_sds_for_value_that_exists_pre_sds(self):
        # ARRANGE #
        file_reference = rel_value_definition(
            _value_reference_of_path_with_accepted('VAL_DEF_NAME',
                                                   RelOptionType.REL_HOME),
            PathPartAsFixedPath('file.txt'))
        value_definitions = singleton_symbol_table(
            v2.entry('VAL_DEF_NAME',
                     v2.file_ref_value(file_ref=sut.rel_home(PathPartAsFixedPath('file-name')))))
        # ASSERT #
        self.assertTrue(file_reference.exists_pre_sds(value_definitions),
                        'File is expected to exist pre SDS')

    def test_exists_pre_sds_for_value_that_does_not_exist_pre_sds(self):
        # ARRANGE #
        file_reference = rel_value_definition(
            _value_reference_of_path_with_accepted('VAL_DEF_NAME',
                                                   RelOptionType.REL_TMP),
            PathPartAsFixedPath('file.txt'))
        value_definitions = singleton_symbol_table(
            v2.entry('VAL_DEF_NAME',
                     v2.file_ref_value(file_ref=sut.rel_tmp_user(PathPartAsFixedPath('file-name')))))
        # ASSERT #
        self.assertFalse(file_reference.exists_pre_sds(value_definitions),
                         'File is expected to not exist pre SDS')

    def test_existing_file__pre_sds(self):
        referenced_entry = v2.entry('rel_home_path_value',
                                    v2.file_ref_value(file_ref=sut.rel_home(PathPartAsFixedPath('home-sub-dir'))))
        file_reference = rel_value_definition(
            _value_reference_of_path_with_accepted(referenced_entry.key,
                                                   RelOptionType.REL_HOME),
            PathPartAsFixedPath('file.txt'))
        with home_and_sds_with_act_as_curr_dir(
                home_dir_contents=DirContents([
                    Dir('home-sub-dir', [
                        empty_file('file.txt')
                    ])
                ])) as home_and_sds:
            value_definitions = singleton_symbol_table(referenced_entry)
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, value_definitions)
            self.assertTrue(file_reference.file_path_pre_sds(environment).exists())
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_existing_file__post_sds(self):
        referenced_entry = v2.entry('rel_tmp_user_path_value',
                                    v2.file_ref_value(file_ref=sut.rel_tmp_user(
                                        PathPartAsFixedPath('referenced-component'))))
        file_reference = rel_value_definition(
            _value_reference_of_path_with_accepted(referenced_entry.key,
                                                   RelOptionType.REL_TMP),
            PathPartAsFixedPath('file.txt'))
        with home_and_sds_with_act_as_curr_dir(
                sds_contents=tmp_user_dir_contents(DirContents([
                    Dir('referenced-component', [
                        empty_file('file.txt')
                    ])]))) as home_and_sds:
            value_definitions = singleton_symbol_table(referenced_entry)
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, value_definitions)
            self.assertTrue(file_reference.file_path_post_sds(environment).exists())
            self.assertTrue(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file__pre_sds(self):
        file_reference = rel_value_definition(
            _value_reference_of_path_with_accepted('rel_home_path_value',
                                                   RelOptionType.REL_HOME),
            PathPartAsFixedPath('file.txt'))
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            value_definitions = singleton_symbol_table(
                v2.entry('rel_home_path_value',
                         v2.file_ref_value(file_ref=sut.rel_home(PathPartAsFixedPath('file.txt')))))
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, value_definitions)
            self.assertFalse(file_reference.file_path_pre_sds(environment).exists())
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_non_existing_file__post_sds(self):
        file_reference = rel_value_definition(
            _value_reference_of_path_with_accepted('rel_tmp_user_path_value',
                                                   RelOptionType.REL_TMP),
            PathPartAsFixedPath('file.txt'))
        with home_and_sds_with_act_as_curr_dir() as home_and_sds:
            value_definitions = singleton_symbol_table(
                v2.entry('rel_tmp_user_path_value',
                         v2.file_ref_value(file_ref=sut.rel_tmp_user(PathPartAsFixedPath('file.txt')))))
            environment = PathResolvingEnvironmentPreOrPostSds(home_and_sds, value_definitions)
            self.assertFalse(file_reference.file_path_post_sds(environment).exists())
            self.assertFalse(file_reference.file_path_pre_or_post_sds(environment).exists())

    def test_accumulation_of_path_components_pre_sds(self):
        # ARRANGE #
        referenced_entry = v2.entry('rel_home_path_value',
                                    v2.file_ref_value(file_ref=sut.rel_home(PathPartAsFixedPath('first-component'))))
        file_ref_using_val_ref = rel_value_definition(
            _value_reference_of_path_with_accepted(referenced_entry.key,
                                                   RelOptionType.REL_HOME),
            PathPartAsFixedPath('last-component'))
        value_definitions = singleton_symbol_table(referenced_entry)
        path_resolving_env = PathResolvingEnvironmentPreSds(pathlib.Path('home'),
                                                            value_definitions)
        # ACT #
        actual = file_ref_using_val_ref.file_path_pre_sds(path_resolving_env)
        # ASSERT #
        expected = path_resolving_env.home_dir_path / 'first-component' / 'last-component'
        self.assertEqual(str(expected),
                         str(actual))

    def test_accumulation_of_path_components_post_sds(self):
        # ARRANGE #
        referenced_entry = v2.entry('rel_act_path_value',
                                    v2.file_ref_value(file_ref=sut.rel_act(PathPartAsFixedPath('component-1'))))
        file_ref_using_val_ref = rel_value_definition(
            _value_reference_of_path_with_accepted(referenced_entry.key,
                                                   RelOptionType.REL_ACT),
            PathPartAsFixedPath('component-2'))
        value_definitions = singleton_symbol_table(referenced_entry)
        path_resolving_env = PathResolvingEnvironmentPostSds(SandboxDirectoryStructure('sds'),
                                                             value_definitions)
        # ACT #
        actual = file_ref_using_val_ref.file_path_post_sds(path_resolving_env)
        # ASSERT #
        expected = path_resolving_env.sds.act_dir / 'component-1' / 'component-2'
        self.assertEqual(str(expected),
                         str(actual))


def _value_reference_of_path_with_accepted(value_name: str,
                                           accepted: RelOptionType) -> ValueReference:
    return ValueReference(value_name,
                          FileRefRelativityRestriction(_path_relativity_variants_with(accepted)))


def _path_relativity_variants_with(accepted: RelOptionType) -> PathRelativityVariants:
    return PathRelativityVariants({accepted}, False)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
