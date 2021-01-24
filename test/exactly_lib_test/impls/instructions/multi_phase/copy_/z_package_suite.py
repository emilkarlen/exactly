import unittest
from pathlib import PurePosixPath
from typing import List, Sequence, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.instructions.multi_phase import copy as sut
from exactly_lib.tcfs.path_relativity import RelNonHdsOptionType, RelHdsOptionType
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.instructions.multi_phase.copy_.test_resources import argument_syntax as args
from exactly_lib_test.impls.instructions.multi_phase.copy_.test_resources import case_definitions, defs
from exactly_lib_test.impls.instructions.multi_phase.test_resources import instruction_embryo_check
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation, \
    expectation
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfigurationRelHds, \
    RelativityOptionConfigurationForRelNonHds
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import hds_populators, sds_populator
from exactly_lib_test.tcfs.test_resources.sds_check import sds_contents_check as sds_contents_check
from exactly_lib_test.tcfs.test_resources.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, Dir
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_actions import \
    ChangeDirectoryToDirectory
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestInvalidSyntax(),
        TestIllegalRelativitiesIndependentOfPhase(),
        TestIllegalRelativitiesSpecificForPhasesBeforeAct(),
        TestLegalRelativitiesIndependentOfPhase(),
        TestLegalRelativitiesSpecificForPhasesAfterAct(),
        unittest.makeSuite(TestValidationErrorScenarios),
        unittest.makeSuite(TestFailingScenarios),
        TestSuccessfulScenariosWithSymbolReferences(),
        unittest.makeSuite(TestSuccessfulScenariosWithoutExplicitDestination),
        unittest.makeSuite(TestSuccessfulScenariosWithExplicitDestination),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name', False)),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name', True)),
    ])


class TestInvalidSyntax(unittest.TestCase):
    def runTest(self):
        for parser_checker in _PARSE_CHECKERS:
            for arguments_case in case_definitions.INVALI_SYNTAX_CASES:
                with self.subTest(parser=parser_checker.name,
                                  arguments=arguments_case.name):
                    parser_checker.value.check_invalid_arguments(self, remaining_source(arguments_case.value))


class TestIllegalRelativitiesIndependentOfPhase(unittest.TestCase):
    def runTest(self):
        for parser_checker in _PARSE_CHECKERS:
            for illegal_case in case_definitions.illegal_relativities_independent_of_phase():
                with self.subTest(parser=parser_checker.name,
                                  illegal_relativity=illegal_case.name):
                    parser_checker.value.check_invalid_arguments(self, illegal_case.value.as_remaining_source)


class TestIllegalRelativitiesSpecificForPhasesBeforeAct(unittest.TestCase):
    def runTest(self):
        for illegal_case in case_definitions.illegal_relativities_specific_for_phase_before_act():
            with self.subTest(illegal_dst=illegal_case.name):
                _PARSE_CHECKER__BEFORE_ACT.check_invalid_arguments(self, illegal_case.value.as_remaining_source)


class TestLegalRelativitiesIndependentOfPhase(unittest.TestCase):
    def runTest(self):
        for parser_checker in _PARSE_CHECKERS:
            for relativity_case in case_definitions.legal_relativities_independent_of_phase():
                with self.subTest(parser=parser_checker.name,
                                  relativities=relativity_case.name):
                    parser_checker.value.check_valid_arguments(self, relativity_case.value.as_remaining_source)


class TestLegalRelativitiesSpecificForPhasesAfterAct(unittest.TestCase):
    def runTest(self):
        for legal_case in case_definitions.legal_relativities_specific_for_phases_after_act():
            with self.subTest(legal_case.name):
                _PARSE_CHECKER__AFTER_ACT.check_valid_arguments(
                    self,
                    legal_case.value.as_remaining_source,
                )


class TestValidationErrorScenarios(unittest.TestCase):
    def test_ERROR_when_file_does_not_exist__without_explicit_destination__hds(self):
        for execution_checker in _EXECUTION_CHECKERS:
            for relativity_option in source_relativity_options__hds():
                with self.subTest(parser=execution_checker.name,
                                  relativity=relativity_option.test_case_description):
                    execution_checker.value.check(
                        self,
                        args.copy(
                            relativity_option.path_argument_of_rel_name('source-that-do-not-exist')
                        ).as_remaining_source,
                        ArrangementWithSds(
                            symbols=relativity_option.symbols.in_arrangement(),
                        ),
                        expectation(
                            validation=ValidationAssertions.pre_sds_fails__w_any_msg(),
                            symbol_usages=relativity_option.symbols.usages_expectation(),
                        ),
                    )

    def test_ERROR_when_file_does_not_exist__with_explicit_destination__hds(self):
        for execution_checker in _EXECUTION_CHECKERS:
            for relativity_option in source_relativity_options__hds():
                with self.subTest(parser=execution_checker.name,
                                  relativity=relativity_option.test_case_description):
                    execution_checker.value.check__w_source_variants(
                        self,
                        args.copy(
                            relativity_option.path_argument_of_rel_name('source-that-do-not-exist'),
                            defs.ARBITRARY_DST_REL_OPT.path_argument_of_rel_name('destination')
                        ).as_str,
                        ArrangementWithSds(
                            symbols=relativity_option.symbols.in_arrangement(),
                        ),
                        expectation(
                            validation=ValidationAssertions.pre_sds_fails__w_any_msg(),
                            symbol_usages=relativity_option.symbols.usages_expectation(),
                        ),
                    )

    def test_ERROR_when_file_does_not_exist__without_explicit_destination__non_hds(self):
        for execution_checker in _EXECUTION_CHECKERS:
            for relativity_option in source_relativity_options__non_hds():
                with self.subTest(parser=execution_checker.name,
                                  relativity=relativity_option.test_case_description):
                    execution_checker.value.check(
                        self,
                        args.copy(
                            relativity_option.path_argument_of_rel_name('source-that-do-not-exist')
                        ).as_remaining_source,
                        ArrangementWithSds(
                            symbols=relativity_option.symbols.in_arrangement(),
                        ),
                        expectation(
                            symbol_usages=relativity_option.symbols.usages_expectation(),
                            validation=ValidationAssertions.post_sds_fails__w_any_msg(),
                        )
                    )

    def test_ERROR_when_src_file_does_not_exist__with_explicit_destination__non_hds(self):
        for execution_checker in _EXECUTION_CHECKERS:
            for src_relativity in source_relativity_options__non_hds():
                with self.subTest(parser=execution_checker.name,
                                  relativity=src_relativity.test_case_description):
                    execution_checker.value.check(
                        self,
                        args.copy(
                            src_relativity.path_argument_of_rel_name('source-that-do-not-exist'),
                            defs.ARBITRARY_DST_REL_OPT.path_argument_of_rel_name('destination')
                        ).as_remaining_source,
                        ArrangementWithSds(
                            symbols=src_relativity.symbols.in_arrangement(),
                        ),
                        expectation(
                            symbol_usages=src_relativity.symbols.usages_expectation(),
                            validation=ValidationAssertions.post_sds_fails__w_any_msg(),
                        )
                    )


class TestSuccessfulScenariosWithoutExplicitDestination(unittest.TestCase):
    def test_copy_file__src_rel_hds(self):
        for execution_checker in _EXECUTION_CHECKERS:
            for src_relativity_option in source_relativity_options__hds():
                with self.subTest(parser=execution_checker.name,
                                  relativity=src_relativity_option.test_case_description):
                    file_arg = src_relativity_option.path_argument_of_rel_name('existing-file')
                    file_to_install = DirContents([(File(file_arg.name,
                                                         'contents'))])
                    execution_checker.value.check(
                        self,
                        args.copy(file_arg).as_remaining_source,
                        ArrangementWithSds(
                            pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                            hds_contents=src_relativity_option.populator_for_relativity_option_root__hds(
                                file_to_install),
                            symbols=src_relativity_option.symbols.in_arrangement(),
                        ),
                        expectation(
                            symbol_usages=src_relativity_option.symbols.usages_expectation(),
                            main_side_effects_on_sds=sds_contents_check.cwd_contains_exactly(file_to_install),
                        )
                    )

    def test_copy_file__src_rel_non_hds(self):
        for execution_checker in _EXECUTION_CHECKERS:
            for relativity_option in source_relativity_options__non_hds():
                with self.subTest(parser=execution_checker.name,
                                  relativity=relativity_option.test_case_description):
                    file_arg = relativity_option.path_argument_of_rel_name('existing-file')
                    file_to_install = DirContents([(File(file_arg.name,
                                                         'contents'))])
                    execution_checker.value.check(
                        self,
                        args.copy(file_arg).as_remaining_source,
                        ArrangementWithSds(
                            pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                            non_hds_contents=relativity_option.populator_for_relativity_option_root__non_hds(
                                file_to_install
                            ),
                            symbols=relativity_option.symbols.in_arrangement(),
                        ),
                        expectation(
                            symbol_usages=relativity_option.symbols.usages_expectation(),
                            main_side_effects_on_sds=sds_contents_check.cwd_contains_exactly(file_to_install),
                        )
                    )

    def test_copy_directory(self):
        src_path_arg = defs.DEFAULT_SRC_REL_OPT.path_argument_of_rel_name('existing-dir')
        files_to_install = DirContents([Dir(src_path_arg.name,
                                            [File('a', 'a'),
                                             Dir('d', []),
                                             Dir('d2',
                                                 [File('f', 'f')])
                                             ])])
        for execution_checker in _EXECUTION_CHECKERS:
            with self.subTest(parser=execution_checker.name):
                execution_checker.value.check(
                    self,
                    args.copy(src_path_arg).as_remaining_source,
                    ArrangementWithSds(
                        pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                        hds_contents=defs.DEFAULT_SRC_REL_OPT.populator_for_relativity_option_root__hds(
                            files_to_install),
                    ),
                    expectation(
                        main_side_effects_on_sds=sds_contents_check.cwd_contains_exactly(
                            files_to_install)
                    )
                )


class TestSuccessfulScenariosWithExplicitDestination(unittest.TestCase):
    def test_copy_file__non_existing_destination(self):
        dst_file_name = 'dst-file_name-file.txt'
        sub_dir_name = 'src-sub-dir'
        source_file_contents = 'contents'
        src_file = File('src-file_name-file.txt', source_file_contents)
        home_dir_contents_cases = [
            (src_file.file_name, DirContents([src_file])),

            (str(PurePosixPath(sub_dir_name) / src_file.file_name),
             DirContents([Dir(sub_dir_name, [src_file])
                          ])),
        ]
        expected_destination_dir_contents = DirContents([File(dst_file_name, src_file.contents)])
        for src_rel_option in source_relativity_options__hds():
            for dst_rel_option in destination_relativity_options():
                for src_argument, home_dir_contents in home_dir_contents_cases:
                    self._sub_test__copy_file(
                        src_rel_option=src_rel_option,
                        dst_rel_option=dst_rel_option,
                        src_file_name=src_argument,
                        dst_file_name=dst_file_name,
                        hds_contents=src_rel_option.populator_for_relativity_option_root__hds(home_dir_contents),
                        sds_populator_before_main=sds_populator.empty(),
                        expected_destination_dir_contents=expected_destination_dir_contents,
                    )

    def test_copy_file__destination_with_multiple_path_components(self):
        source_file = File('src-file_name-file.txt', 'contents')
        home_dir_contents = DirContents([source_file])
        destination_dir_contents_cases = [
            DestinationSetup(
                case_name='two components - non of them exists',
                path_argument_str='sub/leaf',
                dst_relativity_root_contents_arrangement=DirContents([]),
                expected_relativity_root_contents=DirContents([
                    Dir('sub', [
                        File('leaf', source_file.contents)
                    ])
                ]),
            ),
            DestinationSetup(
                case_name='two components - first exists as dir',
                path_argument_str='sub/leaf',
                dst_relativity_root_contents_arrangement=DirContents([Dir.empty('sub')]),
                expected_relativity_root_contents=DirContents([
                    Dir('sub', [
                        File('leaf', source_file.contents)
                    ])
                ]),
            ),
            DestinationSetup(
                case_name='two components - both exist as dirs',
                path_argument_str='sub/leaf',
                dst_relativity_root_contents_arrangement=DirContents([Dir('sub', [Dir.empty('leaf')])]),
                expected_relativity_root_contents=DirContents([
                    Dir('sub', [
                        Dir('leaf', [source_file])
                    ])
                ]),
            ),
        ]
        src_rel_option = rel_opt_conf.default_conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)
        for dst_rel_option in some_destination_relativity_options():
            for destination_setup in destination_dir_contents_cases:
                self._sub_test__copy_file(
                    src_rel_option=src_rel_option,
                    dst_rel_option=dst_rel_option,
                    src_file_name=source_file.file_name,
                    dst_file_name=destination_setup.path_argument_str,
                    hds_contents=src_rel_option.populator_for_relativity_option_root__hds(home_dir_contents),
                    sds_populator_before_main=destination_setup.sds_populator_of_root_of(
                        dst_rel_option,
                        destination_setup.dst_relativity_root_contents_arrangement),
                    expected_destination_dir_contents=destination_setup.expected_relativity_root_contents)

    def _sub_test__copy_file(
            self,
            src_rel_option: rel_opt_conf.RelativityOptionConfigurationRelHds,
            dst_rel_option: rel_opt_conf.RelativityOptionConfigurationForRelNonHds,
            src_file_name: str,
            dst_file_name: str,
            expected_destination_dir_contents: DirContents,
            sds_populator_before_main: sds_populator.SdsPopulator,
            hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
    ):
        arguments = args.copy(src_rel_option.path_argument_of_rel_name(src_file_name),
                              dst_rel_option.path_argument_of_rel_name(dst_file_name))
        for parser_case in _EXECUTION_CHECKERS:
            with self.subTest(parser=parser_case.name,
                              arguments=arguments.as_str):
                symbols_in_arrangement = SymbolContext.symbol_table_of_contexts(
                    src_rel_option.symbols.contexts_for_arrangement() +
                    dst_rel_option.symbols.contexts_for_arrangement()
                )
                expected_symbol_usages = asrt.matches_sequence(
                    src_rel_option.symbols.usage_expectation_assertions() +
                    dst_rel_option.symbols.usage_expectation_assertions()
                )
                parser_case.value.check__w_source_variants(
                    self,
                    arguments.as_str,
                    ArrangementWithSds(
                        pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                        hds_contents=hds_contents,
                        sds_contents=sds_populator_before_main,
                        symbols=symbols_in_arrangement,
                    ),
                    Expectation(
                        symbol_usages=expected_symbol_usages,
                        main_result=asrt.is_none,
                        main_side_effects_on_sds=sds_contents_check.non_hds_dir_contains_exactly(
                            dst_rel_option.root_dir__non_hds,
                            expected_destination_dir_contents),
                    ),
                )

    def test_copy_file__destination_is_existing_directory(self):
        # ARRANGE #
        src = 'src-file'
        dst = 'dst-dir'
        file_to_install = File(src, 'contents')
        home_dir_contents = [file_to_install]
        act_dir_contents = [Dir.empty(dst)]
        act_dir_contents_after = [Dir(dst, [file_to_install])]
        for parser_case in _EXECUTION_CHECKERS:
            with self.subTest(parser=parser_case.name):
                # ACT & ASSERT #
                parser_case.value.check__w_source_variants(
                    self,
                    args.copy(
                        defs.DEFAULT_SRC_REL_OPT.path_argument_of_rel_name(src),
                        defs.DEFAULT_DST_REL_OPT.path_argument_of_rel_name(dst)
                    ).as_str,
                    ArrangementWithSds(
                        pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                        hds_contents=defs.DEFAULT_SRC_REL_OPT.populator_for_relativity_option_root__hds(
                            DirContents(home_dir_contents)
                        ),
                        sds_contents=defs.DEFAULT_DST_REL_OPT.populator_for_relativity_option_root__sds(
                            DirContents(act_dir_contents)
                        ),
                    ),
                    expectation(
                        main_side_effects_on_sds=sds_contents_check.cwd_contains_exactly(
                            DirContents(act_dir_contents_after))
                    ),
                )

    def test_copy_directory__destination_is_existing_directory(self):
        # ARRANGE #
        src_dir = 'existing-dir'
        dst_dir = 'existing-dst-dir'
        files_to_install = [Dir(src_dir,
                                [File('a', 'a'),
                                 Dir('d', []),
                                 Dir('d2',
                                     [File('f', 'f')])
                                 ])]
        cwd_dir_contents_before = DirContents([Dir.empty(dst_dir)])
        cwd_dir_contents_after = DirContents([Dir(dst_dir, files_to_install)])
        for parser_case in _EXECUTION_CHECKERS:
            with self.subTest(parser=parser_case.name):
                # ACT & ASSERT #
                parser_case.value.check__w_source_variants(
                    self,
                    args.copy(
                        defs.DEFAULT_SRC_REL_OPT.path_argument_of_rel_name(src_dir),
                        defs.DEFAULT_DST_REL_OPT.path_argument_of_rel_name(dst_dir)
                    ).as_str,
                    ArrangementWithSds(
                        pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                        hds_contents=defs.DEFAULT_SRC_REL_OPT.populator_for_relativity_option_root__hds(
                            DirContents(files_to_install)
                        ),
                        sds_contents=defs.DEFAULT_DST_REL_OPT.populator_for_relativity_option_root__sds(
                            cwd_dir_contents_before
                        ),
                    ),
                    expectation(
                        main_side_effects_on_sds=sds_contents_check.cwd_contains_exactly(
                            cwd_dir_contents_after)
                    ),
                )


class TestFailingScenarios(unittest.TestCase):
    def test_destination_already_exists__without_explicit_destination(self):
        # ARRANGE #
        file_name = 'existing-file'
        file_to_install = DirContents([(File(file_name,
                                             'contents'))])
        for parser_case in _EXECUTION_CHECKERS:
            with self.subTest(parser=parser_case.name):
                # ACT & ASSERT #
                parser_case.value.check(
                    self,
                    args.copy(
                        defs.DEFAULT_SRC_REL_OPT.path_argument_of_rel_name(file_name)
                    ).as_remaining_source,
                    ArrangementWithSds(
                        pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                        hds_contents=defs.DEFAULT_SRC_REL_OPT.populator_for_relativity_option_root__hds(
                            file_to_install),
                        sds_contents=defs.DEFAULT_DST_REL_OPT.populator_for_relativity_option_root__sds(
                            DirContents([File.empty(file_name)])
                        ),
                    ),
                    expectation(
                        main_result=asrt_text_doc.is_any_text(),
                    )
                )

    def test_destination_already_exists__with_explicit_destination(self):
        src = 'src-file-name.txt'
        dst = 'dst-file-name.txt'
        home_dir_contents = DirContents([(File.empty(src))])
        cwd_dir_contents = DirContents([File.empty(dst)])
        for parser_case in _EXECUTION_CHECKERS:
            with self.subTest(parser=parser_case.name):
                # ACT & ASSERT #
                parser_case.value.check(
                    self,
                    args.copy(
                        defs.DEFAULT_SRC_REL_OPT.path_argument_of_rel_name(src),
                        defs.DEFAULT_DST_REL_OPT.path_argument_of_rel_name(dst)
                    ).as_remaining_source,
                    ArrangementWithSds(
                        pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                        hds_contents=defs.DEFAULT_SRC_REL_OPT.populator_for_relativity_option_root__hds(
                            home_dir_contents),
                        sds_contents=defs.DEFAULT_DST_REL_OPT.populator_for_relativity_option_root__sds(
                            cwd_dir_contents
                        ),
                    ),
                    Expectation(
                        main_result=asrt_text_doc.is_any_text(),
                    ),
                )

    def test_destination_already_exists_in_destination_directory(self):
        src = 'src-file-name'
        dst = 'dst-dir-name'
        home_dir_contents = DirContents([(File.empty(src))])
        cwd_dir_contents = DirContents([Dir(dst,
                                            [File.empty(src)])])
        for parser_case in _EXECUTION_CHECKERS:
            with self.subTest(parser=parser_case.name):
                # ACT & ASSERT #
                parser_case.value.check(
                    self,
                    args.copy(
                        defs.DEFAULT_SRC_REL_OPT.path_argument_of_rel_name(src),
                        defs.DEFAULT_DST_REL_OPT.path_argument_of_rel_name(dst)
                    ).as_remaining_source,
                    ArrangementWithSds(
                        pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                        hds_contents=defs.DEFAULT_SRC_REL_OPT.populator_for_relativity_option_root__hds(
                            home_dir_contents),
                        sds_contents=defs.DEFAULT_DST_REL_OPT.populator_for_relativity_option_root__sds(
                            cwd_dir_contents
                        ),
                    ),
                    Expectation(
                        main_result=asrt_text_doc.is_any_text(),
                    ),
                )


class TestSuccessfulScenariosWithSymbolReferences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        dst_file_name = 'dst-file_name-file.txt'
        src_file = File('src-file_name-file.txt', 'contents')
        home_dir_contents = DirContents([src_file])
        expected_destination_dir_contents = DirContents([File(dst_file_name, src_file.contents)])

        dst_rel_option = rel_opt_conf.symbol_conf_rel_non_hds(
            defs.ARBITRARY_LEGAL_RELATIVITY__DST__NON_HDS,
            'DST_SYMBOL',
            defs.PATH_RELATIVITY_VARIANTS__DST,
        )
        for phase_is_after_act in [False, True]:
            with self.subTest(phase_is_after_act=phase_is_after_act):
                checker = instruction_embryo_check.Checker(sut.EmbryoParser(phase_is_after_act))
                src_rel_option = rel_opt_conf.symbol_conf_rel_hds(
                    defs.ARBITRARY_LEGAL_RELATIVITY__SRC__HDS,
                    'SRC_SYMBOL',
                    defs.path_relativity_variants__src(phase_is_after_act),
                )
                # ACT & ASSERT #
                checker.check(
                    self,
                    args.copy(src_rel_option.path_argument_of_rel_name(src_file.name),
                              dst_rel_option.path_argument_of_rel_name(dst_file_name)
                              ).as_remaining_source,
                    ArrangementWithSds(
                        hds_contents=src_rel_option.populator_for_relativity_option_root__hds(home_dir_contents),
                        symbols=SymbolContext.symbol_table_of_contexts(
                            src_rel_option.symbols.contexts_for_arrangement() +
                            dst_rel_option.symbols.contexts_for_arrangement()
                        )
                    ),
                    expectation(
                        symbol_usages=asrt.matches_sequence(
                            src_rel_option.symbols.usage_expectation_assertions() +
                            dst_rel_option.symbols.usage_expectation_assertions()
                        ),
                        main_side_effects_on_sds=sds_contents_check.non_hds_dir_contains_exactly(
                            dst_rel_option.root_dir__non_hds,
                            expected_destination_dir_contents),

                    ),
                )


def source_relativity_options__hds() -> List[RelativityOptionConfigurationRelHds]:
    return [
        rel_opt_conf.default_conf_rel_hds(RelHdsOptionType.REL_HDS_CASE),
        rel_opt_conf.conf_rel_hds(RelHdsOptionType.REL_HDS_CASE),
        rel_opt_conf.conf_rel_hds(RelHdsOptionType.REL_HDS_ACT),
    ]


def source_relativity_options__non_hds() -> List[RelativityOptionConfigurationForRelNonHds]:
    return [
        rel_opt_conf.conf_rel_non_hds(RelNonHdsOptionType.REL_ACT),
        rel_opt_conf.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP),
    ]


def destination_relativity_options() -> List[RelativityOptionConfigurationForRelNonHds]:
    return [
        rel_opt_conf.default_conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
        rel_opt_conf.conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
        rel_opt_conf.conf_rel_non_hds(RelNonHdsOptionType.REL_ACT),
        rel_opt_conf.conf_rel_non_hds(RelNonHdsOptionType.REL_TMP),
    ]


def some_destination_relativity_options() -> List[RelativityOptionConfigurationForRelNonHds]:
    return [
        rel_opt_conf.conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
        rel_opt_conf.conf_rel_non_hds(RelNonHdsOptionType.REL_ACT),
    ]


CWD_RESOLVER = SdsSubDirResolverFromSdsFun(SandboxDs.internal_tmp_dir.fget)
MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY = ChangeDirectoryToDirectory(CWD_RESOLVER)


class DestinationSetup:
    def __init__(self,
                 case_name: str,
                 path_argument_str: str,
                 dst_relativity_root_contents_arrangement: DirContents,
                 expected_relativity_root_contents: DirContents,
                 ):
        self.case_name = case_name
        self.dst_relativity_root_contents_arrangement = dst_relativity_root_contents_arrangement
        self.path_argument_str = path_argument_str
        self.expected_relativity_root_contents = expected_relativity_root_contents

    def sds_populator_of_root_of(self,
                                 destination_rel_opt: rel_opt_conf.RelativityOptionConfigurationForRelNonHds,
                                 contents: DirContents,
                                 ) -> sds_populator.SdsPopulator:
        return sds_populator.contents_in_resolved_dir(
            sds_populator.SdsSubDirResolverFromSdsFun(destination_rel_opt.root_dir__non_hds),
            contents,
        )


_PARSER__BEFORE_ACT = sut.EmbryoParser(False)
_PARSER__AFTER_ACT = sut.EmbryoParser(True)

_PARSE_CHECKER__BEFORE_ACT = parse_checker.Checker(_PARSER__BEFORE_ACT)
_PARSE_CHECKER__AFTER_ACT = parse_checker.Checker(_PARSER__AFTER_ACT)

_EXECUTION_CHECKER__BEFORE_ACT = instruction_embryo_check.Checker(_PARSER__BEFORE_ACT)
_EXECUTION_CHECKER__AFTER_ACT = instruction_embryo_check.Checker(_PARSER__AFTER_ACT)

_PARSERS = [
    NameAndValue('before act',
                 _PARSER__BEFORE_ACT
                 ),
    NameAndValue('after act',
                 _PARSER__AFTER_ACT
                 ),
]

_PARSE_CHECKERS = [
    NameAndValue('before act',
                 _PARSE_CHECKER__BEFORE_ACT
                 ),
    NameAndValue('after act',
                 _PARSE_CHECKER__AFTER_ACT
                 ),
]


def __execution_checkers() -> Sequence[NameAndValue[instruction_embryo_check.Checker[Optional[TextRenderer]]]]:
    return [
        NameAndValue('before act',
                     _EXECUTION_CHECKER__BEFORE_ACT
                     ),
        NameAndValue('after act',
                     _EXECUTION_CHECKER__AFTER_ACT
                     ),
    ]


_EXECUTION_CHECKERS = __execution_checkers()

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
