import unittest

from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions.new_dir import RELATIVITY_VARIANTS
from exactly_lib.instructions.setup import new_dir as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util import symbol_table
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import new_dir_instruction_test
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.new_dir_instruction_test import \
    Configuration
from exactly_lib_test.instructions.setup.test_resources.configuration import SetupConfigurationBase
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.symbol.test_resources.concrete_restriction_assertion import \
    equals_file_ref_relativity_restriction
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.symbol.test_resources.symbol_utils import file_ref_value_container, \
    symbol_table_from_entries
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    tmp_user_dir_contains_exactly
from exactly_lib_test.test_resources.file_structure import DirContents, Dir, empty_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class TheConfiguration(SetupConfigurationBase, Configuration):
    def instruction_setup(self) -> SingleInstructionSetup:
        return sut.setup('instruction name')

    def expect_failure_to_create_dir(self):
        return Expectation(main_result=sh_check.is_hard_error())


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        new_dir_instruction_test.suite_for(TheConfiguration()),
        unittest.makeSuite(TestCasesThatTestIntegrationOfValueDefinitionByAFewRandomTests),
    ])


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.setup('instr-name'), source, arrangement, expectation)


class TestCasesThatTestIntegrationOfValueDefinitionByAFewRandomTests(TestCaseBaseForParser):
    def test_symbol_with_relativity_that_is_not_default_relativity(self):
        instruction_argument = '--rel SYMBOL_NAME new-dir-name'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(
                          symbols=symbol_table_from_entries([
                              symbol_table.Entry('SYMBOL_NAME',
                                                 file_ref_value_container(
                                                     file_refs.rel_tmp_user(
                                                         PathPartAsFixedPath('symbol-def-path-arg'))))])
                      ),
                      Expectation(
                          main_side_effects_on_files=tmp_user_dir_contains_exactly(DirContents([
                              Dir('symbol-def-path-arg',
                                  [empty_dir('new-dir-name')])
                          ])),
                          symbol_usages=asrt.matches_sequence([
                              equals_symbol_reference('SYMBOL_NAME',
                                                      equals_file_ref_relativity_restriction(
                                                         FileRefRelativityRestriction(RELATIVITY_VARIANTS)))
                          ]),

                      )
                      )

    def test_WHEN_no_symbol_reference_THEN_no_symbol_usages(self):
        instruction_argument = '--rel-tmp new-dir-name'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(),
                      Expectation(symbol_usages=asrt.is_empty),
                      )
