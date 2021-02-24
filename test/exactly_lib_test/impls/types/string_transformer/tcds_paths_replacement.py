import pathlib
import tempfile
import unittest
from contextlib import contextmanager
from typing import ContextManager, List

from exactly_lib.definitions import path
from exactly_lib.impls.types.string_transformer.impl import tcds_paths_replacement as sut
from exactly_lib.tcfs import tcds_symbols
from exactly_lib.tcfs.hds import HomeDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.resolving_environment import FullResolvingEnvironment
from exactly_lib.util.str_.misc_formatting import with_appended_new_lines
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.string_transformer.test_resources import argument_syntax as args, \
    may_dep_on_ext_resources, freeze_check
from exactly_lib_test.impls.types.string_transformer.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformer.test_resources.integration_check import \
    expectation_of_successful_execution_2
from exactly_lib_test.impls.types.string_transformer.test_resources.replace_tcds_dirs import \
    ReplacedSymbolsFileContentsGeneratorForSubDirRelationshipBetweenHdsActAndCase, \
    ReplacedSymbolsFileContentsGeneratorWithAllReplacedVariables
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.tcfs.test_resources.sds_check.sds_utils import sandbox_directory_structure
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.string_source.test_resources import string_sources


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestMisc),
        unittest.makeSuite(TestSubDirRelationshipBetweenHdsActAndHdsCase),
        unittest.makeSuite(TestWhenRelHdsCaseIsEqualToRelHdsActThenVariableWithPrecedenceShouldBeUsed),
        TestIntegration(),
        TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(),
    ])


class TestMayDependOnExternalResourcesShouldBeThatOfSourceModel(
    may_dep_on_ext_resources.TestMayDepOnExtResourcesShouldBeThatOfSourceModelBase):
    def argument_cases(self) -> List[str]:
        return [args.tcds_path_replacement()]


def _transform_string_to_string(tcds: TestCaseDs, string_input: str) -> str:
    transformer = sut.TcdsPathsReplacementStringTransformer('arbitrary custom', tcds)
    model = string_sources.of_string(string_input)
    output = transformer.transform(model)
    return output.contents().as_str


class TestIntegration(unittest.TestCase):
    def runTest(self):
        def model(environment: FullResolvingEnvironment) -> string_sources.StringSource:
            return string_sources.of_lines__w_check_for_validity(
                self,
                with_appended_new_lines([
                    str(environment.tcds.hds.case_dir),
                    str(environment.tcds.hds.act_dir),
                    str(environment.tcds.sds.act_dir),
                    str(environment.tcds.sds.user_tmp_dir),
                ]),
                environment.application_environment.tmp_files_space.sub_dir_space()
            )

        expected = with_appended_new_lines([
            path.EXACTLY_DIR__REL_HDS_CASE,
            path.EXACTLY_DIR__REL_HDS_ACT,
            path.EXACTLY_DIR__REL_ACT,
            path.EXACTLY_DIR__REL_TMP,
        ])

        integration_check.CHECKER__PARSE_SIMPLE.check__w_source_variants(
            self,
            Arguments(args.tcds_path_replacement()),
            model,
            arrangement_w_tcds(),
            expectation_of_successful_execution_2(
                symbol_references=asrt.is_empty_sequence,
                output_lines=expected,
                may_depend_on_external_resources=False,
                is_identity_transformer=False,
                adv=freeze_check.first_invoked_method_of_source_model__is_freeze,
            )
        )


class TestMisc(unittest.TestCase):
    def test_all_variables(self):
        # ARRANGE #
        with tcds_with_act_as_curr_dir() as path_resolving_env_pre_or_post_sds:
            tcds = path_resolving_env_pre_or_post_sds.tcds
            generator = ReplacedSymbolsFileContentsGeneratorWithAllReplacedVariables()
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
            with _with_a_non_root_dir() as a_dir:
                hds = HomeDs(case_dir=a_dir,
                             act_dir=a_dir)
                tcds = TestCaseDs(hds, sds)
                contents_before_replacement = str(a_dir)
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
            with _with_a_non_root_dir() as a_dir:
                hds = HomeDs(case_dir=a_dir.parent,
                             act_dir=a_dir)
                tcds = TestCaseDs(hds, sds)
                generator = ReplacedSymbolsFileContentsGeneratorForSubDirRelationshipBetweenHdsActAndCase(
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
            with _with_a_non_root_dir() as a_dir:
                hds = HomeDs(case_dir=a_dir,
                             act_dir=a_dir.parent)
                tcds = TestCaseDs(hds, sds)
                generator = ReplacedSymbolsFileContentsGeneratorForSubDirRelationshipBetweenHdsActAndCase(
                    name_of_parent_dir__rel_hds_symbol=tcds_symbols.SYMBOL_HDS_ACT,
                    name_of_sub_dir__rel_hds_symbol=tcds_symbols.SYMBOL_HDS_CASE,
                )
                # ACT #
                actual = _transform_string_to_string(tcds, generator.contents_before_replacement(tcds))
                # ASSERT #
                expected = generator.expected_contents_after_replacement(tcds)
                self.assertEqual(expected,
                                 actual)


@contextmanager
def _with_a_non_root_dir() -> ContextManager[pathlib.Path]:
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        yield pathlib.Path(tmp_dir_name) / 'sub'
