import unittest

from exactly_lib.instructions.setup import install as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_file_structure.path_relativity import RelNonHomeOptionType, RelHomeOptionType
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources import relativity_options as rel_opt_conf
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, \
    equivalent_source_variants__with_source_check
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_file_structure.test_resources.home_populators import case_home_dir_contents
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_contents_check as sds_contents_check
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import SdsSubDirResolverFromSdsFun
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.file_structure import DirContents, File, Dir, empty_file, empty_dir
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_actions import \
    ChangeDirectoryToDirectory
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.symbol_tables import symbol_table_from_entries


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestValidationErrorScenarios),
        unittest.makeSuite(TestFailingScenarios),
        unittest.makeSuite(TestSuccessfulScenariosWithoutExplicitDestination),
        unittest.makeSuite(TestSuccessfulScenariosWithExplicitDestination),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestParse(unittest.TestCase):
    def test_fail_when_there_is_no_arguments(self):
        instruction_argument = ''
        for source in equivalent_source_variants(self, instruction_argument):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                sut.Parser().parse(source)

    def test_fail_when_there_is_more_than_two_arguments(self):
        instruction_argument = 'argument1 argument2 argument3'
        for source in equivalent_source_variants(self, instruction_argument):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                sut.Parser().parse(source)

    def test_succeed_when_there_is_exactly_one_argument(self):
        instruction_argument = 'single-argument'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            sut.Parser().parse(source)

    def test_succeed_when_there_is_exactly_two_arguments(self):
        instruction_argument = 'argument1 argument2'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            sut.Parser().parse(source)

    def test_argument_shall_be_parsed_using_shell_syntax(self):
        instruction_argument = "'argument 1' 'argument 2'"
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            sut.Parser().parse(source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             instruction_argument: str,
             arrangement: Arrangement,
             expectation: Expectation):
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._check(sut.Parser(), source, arrangement, expectation)


class TestValidationErrorScenarios(TestCaseBaseForParser):
    def test_ERROR_when_file_does_not_exist__without_explicit_destination(self):
        for relativity_option in source_relativity_options('SOURCE_SYMBOL_NAME'):
            with self.subTest(msg=relativity_option.test_case_description):
                self._run('{relativity_option} source-that-do-not-exist'.format(
                    relativity_option=relativity_option.option_string),
                    Arrangement(
                        symbols=relativity_option.symbols.in_arrangement(),
                    ),
                    Expectation(
                        pre_validation_result=svh_assertions.is_validation_error(),
                        symbol_usages=relativity_option.symbols.usages_expectation(),
                    ))

    def test_ERROR_when_file_does_not_exist__with_explicit_destination(self):
        for relativity_option in source_relativity_options('SOURCE_SYMBOL_NAME'):
            with self.subTest(msg=relativity_option.test_case_description):
                self._run('{relativity_option} source-that-do-not-exist destination'.format(
                    relativity_option=relativity_option.option_string),
                    Arrangement(
                        symbols=relativity_option.symbols.in_arrangement(),
                    ),
                    Expectation(
                        pre_validation_result=svh_assertions.is_validation_error(),
                        symbol_usages=relativity_option.symbols.usages_expectation(),
                    ))


class TestSuccessfulScenariosWithoutExplicitDestination(TestCaseBaseForParser):
    def test_install_file(self):
        for relativity_option in source_relativity_options('SOURCE_SYMBOL_NAME'):
            with self.subTest(msg=relativity_option.test_case_description):
                file_name = 'existing-file'
                arguments = '{relativity_option} {source_file}'.format(
                    relativity_option=relativity_option.option_string,
                    source_file=file_name,
                )
                file_to_install = DirContents([(File(file_name,
                                                     'contents'))])
                self._run(arguments,
                          Arrangement(
                              pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                              hds_contents=case_home_dir_contents(file_to_install),
                              symbols=relativity_option.symbols.in_arrangement(),
                          ),
                          Expectation(
                              main_side_effects_on_files=sds_contents_check.cwd_contains_exactly(file_to_install),
                              symbol_usages=relativity_option.symbols.usages_expectation(),
                          )
                          )

    def test_install_directory(self):
        src_dir = 'existing-dir'
        files_to_install = DirContents([Dir(src_dir,
                                            [File('a', 'a'),
                                             Dir('d', []),
                                             Dir('d2',
                                                 [File('f', 'f')])
                                             ])])
        self._run(src_dir,
                  Arrangement(
                      pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                      hds_contents=case_home_dir_contents(files_to_install),
                  ),
                  Expectation(main_side_effects_on_files=sds_contents_check.cwd_contains_exactly(
                      files_to_install))
                  )


class TestSuccessfulScenariosWithExplicitDestination(TestCaseBaseForParser):
    def test_install_file__non_existing_destination(self):
        dst_file_name = 'dst-file_name-file.txt'
        sub_dir_name = 'src-sub-dir'
        source_file_contents = 'contents'
        src_file = File('src-file_name-file.txt', source_file_contents)
        home_dir_contents_cases = [
            (src_file.file_name, DirContents([src_file])),

            ('{dir_name}/{base_name}'.format(dir_name=sub_dir_name, base_name=src_file.file_name),
             DirContents([Dir(sub_dir_name, [src_file])
                          ])),
        ]
        expected_destination_dir_contents = DirContents([File(dst_file_name, src_file.contents)])
        for src_rel_option in source_relativity_options('SOURCE_SYMBOL_NAME'):
            for dst_rel_option in destination_relativity_options('DESTINATION_SYMBOL_NAME'):
                for src_argument, home_dir_contents in home_dir_contents_cases:
                    self._sub_test__install_file(
                        src_rel_option=src_rel_option,
                        dst_rel_option=dst_rel_option,
                        src_file_name=src_argument,
                        dst_file_name=dst_file_name,
                        hds_contents=case_home_dir_contents(home_dir_contents),
                        sds_populator_before_main=sds_populator.empty(),
                        expected_destination_dir_contents=expected_destination_dir_contents)

    def test_install_file__destination_with_multiple_path_components(self):
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
                dst_relativity_root_contents_arrangement=DirContents([empty_dir('sub')]),
                expected_relativity_root_contents=DirContents([
                    Dir('sub', [
                        File('leaf', source_file.contents)
                    ])
                ]),
            ),
            DestinationSetup(
                case_name='two components - both exist as dirs',
                path_argument_str='sub/leaf',
                dst_relativity_root_contents_arrangement=DirContents([Dir('sub', [empty_dir('leaf')])]),
                expected_relativity_root_contents=DirContents([
                    Dir('sub', [
                        Dir('leaf', [source_file])
                    ])
                ]),
            ),
        ]
        src_rel_option = rel_opt_conf.default_conf_rel_home(RelHomeOptionType.REL_HOME_CASE)
        for dst_rel_option in some_destination_relativity_options():
            for destination_setup in destination_dir_contents_cases:
                self._sub_test__install_file(
                    src_rel_option=src_rel_option,
                    dst_rel_option=dst_rel_option,
                    src_file_name=source_file.file_name,
                    dst_file_name=destination_setup.path_argument_str,
                    hds_contents=case_home_dir_contents(home_dir_contents),
                    sds_populator_before_main=destination_setup.sds_populator_of_root_of(
                        dst_rel_option,
                        destination_setup.dst_relativity_root_contents_arrangement),
                    expected_destination_dir_contents=destination_setup.expected_relativity_root_contents)

    def _sub_test__install_file(
            self,
            src_rel_option: rel_opt_conf.RelativityOptionConfigurationRelHome,
            dst_rel_option: rel_opt_conf.RelativityOptionConfigurationForRelNonHome,
            src_file_name: str,
            dst_file_name: str,
            expected_destination_dir_contents: DirContents,
            sds_populator_before_main: sds_populator.SdsPopulator,
            hds_contents: home_populators.HomePopulator = home_populators.empty(),
    ):
        test_case_name = 'src_file_name={}  src_rel_option={}  dst_rel_option={}'.format(
            src_file_name,
            src_rel_option.test_case_description,
            dst_rel_option.test_case_description)
        with self.subTest(msg=test_case_name):
            arguments = '{src_relativity_option} {src_file} {dst_relativity_option} {dst_file}'.format(
                src_relativity_option=src_rel_option.option_string,
                src_file=src_file_name,
                dst_relativity_option=dst_rel_option.option_string,
                dst_file=dst_file_name,
            )
            symbols_in_arrangement = symbol_table_from_entries(
                src_rel_option.symbols.entries_for_arrangement() +
                dst_rel_option.symbols.entries_for_arrangement()
            )
            expected_symbol_usages = asrt.matches_sequence(
                src_rel_option.symbols.usage_expectation_assertions() +
                dst_rel_option.symbols.usage_expectation_assertions()
            )
            self._check(sut.Parser(),
                        remaining_source(arguments),
                        Arrangement(
                            pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                            hds_contents=hds_contents,
                            sds_contents_before_main=sds_populator_before_main,
                            symbols=symbols_in_arrangement,
                        ),
                        Expectation(
                            main_side_effects_on_files=sds_contents_check.non_home_dir_contains_exactly(
                                dst_rel_option.root_dir__non_home,
                                expected_destination_dir_contents),
                            symbol_usages=expected_symbol_usages,
                        )
                        )

    def test_install_file__destination_is_existing_directory(self):
        src = 'src-file'
        dst = 'dst-dir'
        file_to_install = File(src, 'contents')
        home_dir_contents = [file_to_install]
        act_dir_contents = [empty_dir(dst)]
        act_dir_contents_after = [Dir(dst, [file_to_install])]
        self._run('{} {}'.format(src, dst),
                  Arrangement(
                      pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                      hds_contents=case_home_dir_contents(DirContents(home_dir_contents)),
                      sds_contents_before_main=sds_populator.contents_in_resolved_dir(CWD_RESOLVER,
                                                                                      DirContents(act_dir_contents)),
                  ),
                  Expectation(
                      main_side_effects_on_files=sds_contents_check.cwd_contains_exactly(
                          DirContents(act_dir_contents_after)))
                  )

    def test_install_directory__destination_is_existing_directory(self):
        src_dir = 'existing-dir'
        dst_dir = 'existing-dst-dir'
        files_to_install = [Dir(src_dir,
                                [File('a', 'a'),
                                 Dir('d', []),
                                 Dir('d2',
                                     [File('f', 'f')])
                                 ])]
        cwd_dir_contents_before = DirContents([empty_dir(dst_dir)])
        cwd_dir_contents_after = DirContents([Dir(dst_dir, files_to_install)])
        self._run('{} {}'.format(src_dir, dst_dir),
                  Arrangement(
                      pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                      hds_contents=case_home_dir_contents(DirContents(files_to_install)),
                      sds_contents_before_main=sds_populator.contents_in_resolved_dir(CWD_RESOLVER,
                                                                                      cwd_dir_contents_before),
                  ),
                  Expectation(
                      main_side_effects_on_files=sds_contents_check.cwd_contains_exactly(
                          cwd_dir_contents_after))
                  )


class TestFailingScenarios(TestCaseBaseForParser):
    def test_destination_already_exists__without_explicit_destination(self):
        file_name = 'existing-file'
        file_to_install = DirContents([(File(file_name,
                                             'contents'))])
        self._run(file_name,
                  Arrangement(
                      pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                      hds_contents=case_home_dir_contents(file_to_install),
                      sds_contents_before_main=sds_populator.contents_in_resolved_dir(CWD_RESOLVER,
                                                                                      DirContents(
                                                                                          [empty_file(file_name)])),
                  ),
                  Expectation(
                      main_result=sh_assertions.is_hard_error())
                  )

    def test_destination_already_exists__with_explicit_destination(self):
        src = 'src-file-name.txt'
        dst = 'dst-file-name.txt'
        home_dir_contents = DirContents([(empty_file(src))])
        cwd_dir_contents = DirContents([empty_file(dst)])
        self._run('{} {}'.format(src, dst),
                  Arrangement(
                      pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                      hds_contents=case_home_dir_contents(home_dir_contents),
                      sds_contents_before_main=sds_populator.contents_in_resolved_dir(CWD_RESOLVER,
                                                                                      cwd_dir_contents),
                  ),
                  Expectation(
                      main_result=sh_assertions.is_hard_error()
                  )
                  )

    def test_destination_already_exists_in_destination_directory(self):
        src = 'src-file-name'
        dst = 'dst-dir-name'
        home_dir_contents = DirContents([(empty_file(src))])
        cwd_dir_contents = DirContents([Dir(dst,
                                            [empty_file(src)])])
        self._run('{} {}'.format(src, dst),
                  Arrangement(
                      pre_contents_population_action=MAKE_SUB_DIR_OF_SDS_CURRENT_DIRECTORY,
                      hds_contents=case_home_dir_contents(home_dir_contents),
                      sds_contents_before_main=sds_populator.contents_in_resolved_dir(CWD_RESOLVER,
                                                                                      cwd_dir_contents),
                  ),
                  Expectation(
                      main_result=sh_assertions.is_hard_error())
                  )


def source_relativity_options(symbol_name: str) -> list:
    return [
        rel_opt_conf.default_conf_rel_home(RelHomeOptionType.REL_HOME_CASE),
        rel_opt_conf.conf_rel_home(RelHomeOptionType.REL_HOME_CASE),
        rel_opt_conf.symbol_conf_rel_home(
            RelHomeOptionType.REL_HOME_CASE,
            symbol_name,
            sut.REL_OPTION_ARG_CONF_FOR_SOURCE.options.accepted_relativity_variants),
    ]


def destination_relativity_options(symbol_name: str) -> list:
    return [
        rel_opt_conf.default_conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
        rel_opt_conf.conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
        rel_opt_conf.conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
        rel_opt_conf.conf_rel_non_home(RelNonHomeOptionType.REL_TMP),
        rel_opt_conf.symbol_conf_rel_non_home(
            RelNonHomeOptionType.REL_CWD,
            symbol_name,
            sut.REL_OPTION_ARG_CONF_FOR_DESTINATION.options.accepted_relativity_variants),
        rel_opt_conf.symbol_conf_rel_non_home(
            RelNonHomeOptionType.REL_TMP,
            symbol_name,
            sut.REL_OPTION_ARG_CONF_FOR_DESTINATION.options.accepted_relativity_variants),
    ]


def some_destination_relativity_options() -> list:
    return [
        rel_opt_conf.conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
        rel_opt_conf.conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
    ]


CWD_RESOLVER = SdsSubDirResolverFromSdsFun(lambda sds: sds.tmp.internal_dir)
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
                                 destination_rel_opt: rel_opt_conf.RelativityOptionConfigurationForRelNonHome,
                                 contents: DirContents,
                                 ) -> sds_populator.SdsPopulator:
        return sds_populator.contents_in_resolved_dir(
            sds_populator.SdsSubDirResolverFromSdsFun(destination_rel_opt.root_dir__non_home),
            contents,
        )


if __name__ == '__main__':
    unittest.main()
