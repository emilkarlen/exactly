import pathlib
import unittest

from exactly_lib.test_case_file_structure import environment_variables
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_utils.lines_transformers import env_vars_replacement as sut
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import sandbox_directory_structure
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.replaced_env_vars import \
    ReplacedEnvVarsFileContentsGeneratorForSubDirRelationshipBetweenHomeActAndCase, \
    ReplacedEnvVarsFileContentsGeneratorWithAllReplacedVariables
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    home_and_sds_with_act_as_curr_dir


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMisc),
        unittest.makeSuite(TestSubDirRelationshipBetweenHomeActAndHomeCase),
        unittest.makeSuite(TestWhenRelHomeCaseIsEqualToRelHomeActThenVariableWithPrecedenceShouldBeUsed),
    ])


class TestMisc(unittest.TestCase):
    def test_all_variables(self):
        # ARRANGE #
        with home_and_sds_with_act_as_curr_dir() as path_resolving_env_pre_or_post_sds:
            home_and_sds = path_resolving_env_pre_or_post_sds.home_and_sds
            generator = ReplacedEnvVarsFileContentsGeneratorWithAllReplacedVariables()
            # ACT #
            actual = sut.replace(home_and_sds,
                                 generator.contents_before_replacement(home_and_sds))
            # ASSERT #
            expected = generator.expected_contents_after_replacement(home_and_sds)
            self.assertEqual(expected,
                             actual)


class TestWhenRelHomeCaseIsEqualToRelHomeActThenVariableWithPrecedenceShouldBeUsed(unittest.TestCase):
    def test(self):
        # ARRANGE #
        with sandbox_directory_structure() as sds:
            the_dir = pathlib.Path.cwd()
            hds = HomeDirectoryStructure(case_dir=the_dir,
                                         act_dir=the_dir)
            home_and_sds = HomeAndSds(hds, sds)
            contents_before_replacement = str(the_dir)
            # ACT #
            actual = sut.replace(home_and_sds, contents_before_replacement)
            # ASSERT #
            expected = sut.HOME_ENV_VAR_WITH_REPLACEMENT_PRECEDENCE
            self.assertEqual(expected,
                             actual)


class TestSubDirRelationshipBetweenHomeActAndHomeCase(unittest.TestCase):
    def test_home_act_is_sub_dir_of_home_case(self):
        # ARRANGE #
        with sandbox_directory_structure() as sds:
            a_dir = pathlib.Path.cwd()
            hds = HomeDirectoryStructure(case_dir=a_dir.parent,
                                         act_dir=a_dir)
            home_and_sds = HomeAndSds(hds, sds)
            generator = ReplacedEnvVarsFileContentsGeneratorForSubDirRelationshipBetweenHomeActAndCase(
                name_of_parent_dir__rel_home_env_var=environment_variables.ENV_VAR_HOME_CASE,
                name_of_sub_dir__rel_home_env_var=environment_variables.ENV_VAR_HOME_ACT,
            )
            # ACT #
            actual = sut.replace(home_and_sds, generator.contents_before_replacement(home_and_sds))
            # ASSERT #
            expected = generator.expected_contents_after_replacement(home_and_sds)
            self.assertEqual(expected,
                             actual)

    def test_home_case_is_sub_dir_of_home_act(self):
        # ARRANGE #
        with sandbox_directory_structure() as sds:
            a_dir = pathlib.Path.cwd()
            hds = HomeDirectoryStructure(case_dir=a_dir,
                                         act_dir=a_dir.parent)
            home_and_sds = HomeAndSds(hds, sds)
            generator = ReplacedEnvVarsFileContentsGeneratorForSubDirRelationshipBetweenHomeActAndCase(
                name_of_parent_dir__rel_home_env_var=environment_variables.ENV_VAR_HOME_ACT,
                name_of_sub_dir__rel_home_env_var=environment_variables.ENV_VAR_HOME_CASE,
            )
            # ACT #
            actual = sut.replace(home_and_sds, generator.contents_before_replacement(home_and_sds))
            # ASSERT #
            expected = generator.expected_contents_after_replacement(home_and_sds)
            self.assertEqual(expected,
                             actual)
