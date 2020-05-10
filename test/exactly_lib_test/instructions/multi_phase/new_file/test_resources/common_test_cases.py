import unittest
from typing import Sequence, Iterable

from exactly_lib.instructions.multi_phase import new_file as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol import symbol_syntax
from exactly_lib.test_case_file_structure.path_relativity import RelNonHdsOptionType, RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.utils import IS_FAILURE
from exactly_lib_test.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation, expectation
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources.path import PathDdvSymbolContext
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_file_structure.test_resources import tcds_populators
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import TcdsPopulator
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.test_resources import validation as validation_utils
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_non_hds
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_file, empty_dir, Dir
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: Expectation,
               phase_is_after_act: bool = True,
               ):
        parser = sut.EmbryoParser('instruction-name', phase_is_after_act)
        embryo_check.check(self, parser, source, arrangement, expectation)


class InvalidDestinationFileTestCasesData:
    def __init__(self,
                 file_contents_cases: Sequence[NameAndValue[ArgumentElements]],
                 symbols: SymbolTable,
                 pre_existing_files: TcdsPopulator = tcds_populators.empty(),
                 ):
        self.file_contents_cases = file_contents_cases
        self.symbols = symbols
        self.pre_existing_files = pre_existing_files


class TestCommonFailingScenariosDueToInvalidDestinationFileBase(TestCaseBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        raise NotImplementedError('abstract method')

    def _check_cases_for_dst_file_setup__w_relativity_options(self,
                                                              dst_file_name: str,
                                                              dst_root_contents_before_execution: DirContents,
                                                              ):

        cases_data = self._file_contents_cases()

        dst_file_relativity_cases = [
            conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
            conf_rel_non_hds(RelNonHdsOptionType.REL_ACT),
        ]

        for rel_opt_conf in dst_file_relativity_cases:

            non_hds_contents = rel_opt_conf.populator_for_relativity_option_root__non_hds(
                dst_root_contents_before_execution)

            for file_contents_case in cases_data.file_contents_cases:
                optional_arguments_elements = file_contents_case.value
                optional_arguments = optional_arguments_elements.as_arguments

                with self.subTest(file_contents_variant=file_contents_case.name,
                                  first_line_argments=optional_arguments.first_line,
                                  dst_file_variant=rel_opt_conf.option_argument):
                    source = remaining_source(
                        '{relativity_option_arg} {dst_file_argument} {optional_arguments}'.format(
                            relativity_option_arg=rel_opt_conf.option_argument,
                            dst_file_argument=dst_file_name,
                            optional_arguments=optional_arguments.first_line,
                        ),
                        optional_arguments.following_lines)

                    # ACT & ASSERT #

                    self._check(source,
                                ArrangementWithSds(
                                    pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                                    tcds_contents=cases_data.pre_existing_files,
                                    non_hds_contents=non_hds_contents,
                                    symbols=cases_data.symbols,
                                ),
                                expectation(
                                    main_result=IS_FAILURE,
                                    symbol_usages=asrt.anything_goes(),
                                )
                                )

    def _check_cases_for_dst_file_setup__expect_pre_sds_validation_failure(
            self,
            dst_file_name: str,
            additional_symbols: Iterable[Entry] = (),
    ):

        cases_data = self._file_contents_cases()

        for file_contents_case in cases_data.file_contents_cases:
            optional_arguments_elements = file_contents_case.value
            optional_arguments = optional_arguments_elements.as_arguments

            symbols = cases_data.symbols.copy()
            symbols.add_all(additional_symbols)

            with self.subTest(file_contents_variant=file_contents_case.name,
                              first_line_argments=optional_arguments.first_line):
                source = remaining_source(
                    '{dst_file_argument} {optional_arguments}'.format(
                        dst_file_argument=dst_file_name,
                        optional_arguments=optional_arguments.first_line,
                    ),
                    optional_arguments.following_lines)

                # ACT & ASSERT #

                self._check(source,
                            ArrangementWithSds(
                                symbols=symbols,
                            ),
                            expectation(
                                validation=validation_utils.pre_sds_validation_fails__w_any_msg(),
                                symbol_usages=asrt.anything_goes(),
                            )
                            )

    def test_fail_WHEN_dst_file_is_existing_file(self):
        dst_file_name = 'file.txt'
        self._check_cases_for_dst_file_setup__w_relativity_options(
            dst_file_name,
            DirContents([
                empty_file(dst_file_name)
            ]),
        )

    def test_fail_WHEN_dst_file_is_existing_dir(self):
        dst_file_name = 'dst-dir'
        self._check_cases_for_dst_file_setup__w_relativity_options(
            dst_file_name,
            DirContents([
                empty_dir(dst_file_name)
            ]),
        )

    def test_fail_WHEN_dst_file_is_existing_broken_symlink(self):
        dst_file_name = 'dst-file'
        self._check_cases_for_dst_file_setup__w_relativity_options(
            dst_file_name,
            DirContents([
                fs.sym_link(dst_file_name,
                            'non-existing-symlink-target.txt')
            ]),
        )

    def test_fail_WHEN_dst_file_is_under_path_that_contains_a_component_that_is_an_existing_file(self):
        self._check_cases_for_dst_file_setup__w_relativity_options(
            'existing-dir/existing-file/dst-file-name',
            DirContents([
                Dir('existing-dir', [
                    empty_file('existing-file')
                ])
            ]),
        )

    def test_validation_pre_sds_fails_WHEN_dst_file_is_parent_dir(self):
        invalid_dir_names = [
            '.',
            'dir-name/.',
            '..',
            'dir-name/..',
        ]
        for invalid_dir_name in invalid_dir_names:
            with self.subTest(invalid_dir_name):
                self._check_cases_for_dst_file_setup__expect_pre_sds_validation_failure(
                    invalid_dir_name,
                )

    def test_validation_pre_sds_fails_WHEN_dst_file_tcds_dir(self):
        dst_file_relativity_cases = [
            RelOptionType.REL_CWD,
            RelOptionType.REL_ACT,
        ]

        for dst_file_relativity_case in dst_file_relativity_cases:
            path_symbol_wo_suffix = PathDdvSymbolContext.of_no_suffix(
                'dst_path_symbol',
                dst_file_relativity_case,
            )
            additional_symbol_table_entries = [
                path_symbol_wo_suffix.entry,
            ]
            with self.subTest(dst_file_relativity_case):
                self._check_cases_for_dst_file_setup__expect_pre_sds_validation_failure(
                    symbol_syntax.symbol_reference_syntax_for_name(path_symbol_wo_suffix.name),
                    additional_symbol_table_entries,
                )
