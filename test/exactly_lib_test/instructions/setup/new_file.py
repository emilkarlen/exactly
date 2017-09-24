import unittest

from exactly_lib.instructions.multi_phase_instructions.new_file import RELATIVITY_VARIANTS
from exactly_lib.instructions.setup import new_file as sut
from exactly_lib.named_element.symbol.restrictions.value_restrictions import FileRefRelativityRestriction
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util import symbol_table
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.named_element.symbol.restrictions.test_resources.concrete_restriction_assertion import \
    equals_file_ref_relativity_restriction
from exactly_lib_test.named_element.symbol.test_resources.symbol_reference_assertions import \
    equals_symbol_reference_with_restriction_on_direct_target
from exactly_lib_test.named_element.symbol.test_resources.symbol_utils import file_ref_constant_container
from exactly_lib_test.section_document.test_resources.parse_source import argument_list_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import every_line_is_consumed
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    act_dir_contains_exactly, tmp_user_dir_contains_exactly
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_populator import contents_in
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file, File
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.symbol_tables import symbol_table_from_entries


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationByAFewRandomTests))
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationOfValueDefinitionByAFewRandomTests))
    return ret_val


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.setup('instr-name'), source, arrangement, expectation)


class TestCasesThatTestIntegrationByAFewRandomTests(TestCaseBaseForParser):
    def test_file_in_sub_dir__sub_dir_exists(self):
        instruction_argument = 'existing-directory/file-name.txt'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(sds_contents_before_main=contents_in(RelSdsOptionType.REL_ACT,
                                                                       DirContents([
                                                                           empty_dir('existing-directory')
                                                                       ]))
                                  ),
                      Expectation(main_side_effects_on_sds=act_dir_contains_exactly(DirContents([
                          Dir('existing-directory', [
                              empty_file('file-name.txt')])
                      ])))
                      )

    def test_single_line_contents(self):
        self._run(argument_list_source(['file name', '<<MARKER'],
                                       ['single line',
                                        'MARKER']),
                  Arrangement(),
                  Expectation(main_side_effects_on_sds=act_dir_contains_exactly(DirContents([
                      File('file name',
                           lines_content(['single line']))
                  ])),
                      source=every_line_is_consumed)
                  )

    def test_argument_is_existing_file(self):
        instruction_argument = 'existing-file'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(sds_contents_before_main=contents_in(RelSdsOptionType.REL_ACT,
                                                                       DirContents([
                                                                           empty_file('existing-file')
                                                                       ]))),
                      Expectation(main_result=sh_assertions.is_hard_error())
                      )


class TestCasesThatTestIntegrationOfValueDefinitionByAFewRandomTests(TestCaseBaseForParser):
    def test_symbol_with_relativity_that_is_not_default_relativity(self):
        instruction_argument = '--rel SYMBOL_NAME file-name.txt'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(
                          symbols=symbol_table_from_entries([
                              symbol_table.Entry('SYMBOL_NAME',
                                                 file_ref_constant_container(
                                                     file_refs.rel_tmp_user(
                                                         PathPartAsFixedPath('symbol-def-path-arg'))))])
                      ),
                      Expectation(
                          main_side_effects_on_sds=tmp_user_dir_contains_exactly(DirContents([
                              Dir('symbol-def-path-arg',
                                  [empty_file('file-name.txt')])
                          ])),
                          symbol_usages=asrt.matches_sequence([
                              equals_symbol_reference_with_restriction_on_direct_target('SYMBOL_NAME',
                                                                                        equals_file_ref_relativity_restriction(
                                                                                            FileRefRelativityRestriction(
                                                                                                RELATIVITY_VARIANTS)))
                          ]),
                      )
                      )

    def test_WHEN_no_symbol_reference_THEN_no_symbol_usages(self):
        instruction_argument = '--rel-tmp file-name.txt'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(),
                      Expectation(
                          symbol_usages=asrt.is_empty),
                      )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
