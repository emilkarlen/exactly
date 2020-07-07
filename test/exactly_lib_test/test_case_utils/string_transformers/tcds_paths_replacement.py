import pathlib
import unittest

from exactly_lib.test_case_file_structure import tcds_symbols
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.string_transformer.impl import tcds_paths_replacement as sut
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import sandbox_directory_structure
from exactly_lib_test.test_case_utils.string_transformers.test_resources.replaced_env_vars import \
    ReplacedEnvVarsFileContentsGeneratorForSubDirRelationshipBetweenHdsActAndCase, \
    ReplacedEnvVarsFileContentsGeneratorWithAllReplacedVariables
from exactly_lib_test.test_case_utils.test_resources import string_models
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMisc),
        unittest.makeSuite(TestSubDirRelationshipBetweenHdsActAndHdsCase),
        unittest.makeSuite(TestWhenRelHdsCaseIsEqualToRelHdsActThenVariableWithPrecedenceShouldBeUsed),
    ])


def _transform_string_to_string(tcds: Tcds, string_input: str) -> str:
    transformer = sut.TcdsPathsReplacementStringTransformer('arbitrary custom', tcds)
    model = string_models.of_string(string_input)
    output = transformer.transform__new(model)
    return string_models.as_string(output)


class TestMisc(unittest.TestCase):
    def test_all_variables(self):
        # ARRANGE #
        with tcds_with_act_as_curr_dir() as path_resolving_env_pre_or_post_sds:
            tcds = path_resolving_env_pre_or_post_sds.tcds
            generator = ReplacedEnvVarsFileContentsGeneratorWithAllReplacedVariables()
            # ACT #
            actual = _transform_string_to_string(tcds,
                                                 generator.contents_before_replacement(tcds))
            # ASSERT #
            expected = generator.expected_contents_after_replacement(tcds)
            self.assertEqual(expected,
                             actual)

    def test_SHOULD_not_be_identity_transformer(self):
        transformer = sut.TcdsPathsReplacementStringTransformer('env-var-replacement',
                                                                fake_tcds())
        self.assertFalse(transformer.is_identity_transformer)


class TestWhenRelHdsCaseIsEqualToRelHdsActThenVariableWithPrecedenceShouldBeUsed(unittest.TestCase):
    def test(self):
        # ARRANGE #
        with sandbox_directory_structure() as sds:
            the_dir = pathlib.Path.cwd()
            hds = HomeDirectoryStructure(case_dir=the_dir,
                                         act_dir=the_dir)
            tcds = Tcds(hds, sds)
            contents_before_replacement = str(the_dir)
            # ACT #
            actual = _transform_string_to_string(tcds, contents_before_replacement)
            # ASSERT #
            expected = sut.HDS_PATH_WITH_REPLACEMENT_PRECEDENCE
            self.assertEqual(expected,
                             actual)


class TestSubDirRelationshipBetweenHdsActAndHdsCase(unittest.TestCase):
    def test_hds_act_is_sub_dir_of_hds_case(self):
        # ARRANGE #
        with sandbox_directory_structure() as sds:
            a_dir = pathlib.Path.cwd()
            hds = HomeDirectoryStructure(case_dir=a_dir.parent,
                                         act_dir=a_dir)
            tcds = Tcds(hds, sds)
            generator = ReplacedEnvVarsFileContentsGeneratorForSubDirRelationshipBetweenHdsActAndCase(
                name_of_parent_dir__rel_hds_symbol=tcds_symbols.SYMBOL_HDS_CASE,
                name_of_sub_dir__rel_hds_symbol=tcds_symbols.SYMBOL_HDS_ACT,
            )
            # ACT #
            actual = _transform_string_to_string(tcds, generator.contents_before_replacement(tcds))
            # ASSERT #
            expected = generator.expected_contents_after_replacement(tcds)
            self.assertEqual(expected,
                             actual)

    def test_hds_case_is_sub_dir_of_hds_act(self):
        # ARRANGE #
        with sandbox_directory_structure() as sds:
            a_dir = pathlib.Path.cwd()
            hds = HomeDirectoryStructure(case_dir=a_dir,
                                         act_dir=a_dir.parent)
            tcds = Tcds(hds, sds)
            generator = ReplacedEnvVarsFileContentsGeneratorForSubDirRelationshipBetweenHdsActAndCase(
                name_of_parent_dir__rel_hds_symbol=tcds_symbols.SYMBOL_HDS_ACT,
                name_of_sub_dir__rel_hds_symbol=tcds_symbols.SYMBOL_HDS_CASE,
            )
            # ACT #
            actual = _transform_string_to_string(tcds, generator.contents_before_replacement(tcds))
            # ASSERT #
            expected = generator.expected_contents_after_replacement(tcds)
            self.assertEqual(expected,
                             actual)
