import unittest
from typing import Sequence

from exactly_lib.instructions.multi_phase import new_file as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.path_relativity import RelNonHomeOptionType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.utils import IS_FAILURE
from exactly_lib_test.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_file_structure.test_resources import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomeOrSdsPopulator
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, ArgumentElements
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_non_home
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, Dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
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
                 file_contents_cases: Sequence[NameAndValue[Arguments]],
                 symbols: SymbolTable,
                 pre_existing_files: HomeOrSdsPopulator = home_and_sds_populators.empty(),
                 ):
        self.file_contents_cases = file_contents_cases
        self.symbols = symbols
        self.pre_existing_files = pre_existing_files


class TestCommonFailingScenariosDueToInvalidDestinationFileBase(TestCaseBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        raise NotImplementedError('abstract method')

    def _check_cases_for_dst_file_setup(self,
                                        dst_file_name: str,
                                        dst_root_contents_before_execution: DirContents,
                                        ):

        cases_data = self._file_contents_cases()

        dst_file_relativity_cases = [
            conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
            conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
        ]

        for rel_opt_conf in dst_file_relativity_cases:

            non_home_contents = rel_opt_conf.populator_for_relativity_option_root__non_home(
                dst_root_contents_before_execution)

            for file_contents_case in cases_data.file_contents_cases:
                optional_arguments_elements = file_contents_case.value
                assert isinstance(optional_arguments_elements, ArgumentElements)  # Type info for IDE
                optional_arguments = optional_arguments_elements.as_arguments

                for l in optional_arguments.lines:
                    if l.find('exactly_lib_test') != -1:
                        print(str(optional_arguments.lines))
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
                                    pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                                    home_or_sds_contents=cases_data.pre_existing_files,
                                    non_home_contents=non_home_contents,
                                    symbols=cases_data.symbols,
                                ),
                                Expectation(
                                    main_result=IS_FAILURE,
                                    symbol_usages=asrt.anything_goes(),
                                )
                                )

    def test_fail_WHEN_dst_file_is_existing_file(self):
        dst_file_name = 'file.txt'
        self._check_cases_for_dst_file_setup(
            dst_file_name,
            DirContents([
                empty_file(dst_file_name)
            ]),
        )

    def test_file_WHEN_dst_file_is_existing_dir(self):
        dst_file_name = 'dst-dir'
        self._check_cases_for_dst_file_setup(
            dst_file_name,
            DirContents([
                empty_dir(dst_file_name)
            ]),
        )

    def test_file_WHEN_dst_file_is_existing_broken_symlink(self):
        dst_file_name = 'dst-file'
        self._check_cases_for_dst_file_setup(
            dst_file_name,
            DirContents([
                fs.sym_link(dst_file_name,
                            'non-existing-symlink-target.txt')
            ]),
        )

    def test_fail_WHEN_dst_file_is_under_path_that_contains_a_component_that_is_an_existing_file(self):
        self._check_cases_for_dst_file_setup(
            'existing-dir/existing-file/dst-file-name',
            DirContents([
                Dir('existing-dir', [
                    empty_file('existing-file')
                ])
            ]),
        )
