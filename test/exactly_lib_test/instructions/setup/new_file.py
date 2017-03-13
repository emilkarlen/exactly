import unittest

from exactly_lib.instructions.multi_phase_instructions.new_file import RELATIVITY_VARIANTS
from exactly_lib.instructions.setup import new_file as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case import file_refs
from exactly_lib.test_case.value_definition import ValueReferenceOfPath
from exactly_lib.util import symbol_table
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.section_document.test_resources.parse_source import every_line_is_consumed
from exactly_lib_test.test_case.test_resources.value_definition import symbol_table_from_entries, \
    assert_value_usages_is_singleton_list_with_value_reference, file_ref_value
from exactly_lib_test.test_resources.execution.sds_check.sds_contents_check import act_dir_contains_exactly, \
    tmp_user_dir_contains_exactly
from exactly_lib_test.test_resources.execution.sds_check.sds_populator import act_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file, File
from exactly_lib_test.test_resources.parse import argument_list_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


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
        self._check(sut.Parser(), source, arrangement, expectation)


class TestCasesThatTestIntegrationByAFewRandomTests(TestCaseBaseForParser):
    def test_file_in_sub_dir__sub_dir_exists(self):
        instruction_argument = 'existing-directory/file-name.txt'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(sds_contents_before_main=act_dir_contents(DirContents([
                          empty_dir('existing-directory')
                      ]))
                      ),
                      Expectation(main_side_effects_on_files=act_dir_contains_exactly(DirContents([
                          Dir('existing-directory', [
                              empty_file('file-name.txt')])
                      ])))
                      )

    def test_single_line_contents(self):
        self._run(argument_list_source(['file name', '<<MARKER'],
                                       ['single line',
                                        'MARKER']),
                  Arrangement(),
                  Expectation(main_side_effects_on_files=act_dir_contains_exactly(DirContents([
                      File('file name',
                           lines_content(['single line']))
                  ])),
                      source=every_line_is_consumed)
                  )

    def test_argument_is_existing_file(self):
        instruction_argument = 'existing-file'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(sds_contents_before_main=act_dir_contents(DirContents([
                          empty_file('existing-file')
                      ]))),
                      Expectation(main_result=sh_check.is_hard_error())
                      )


class TestCasesThatTestIntegrationOfValueDefinitionByAFewRandomTests(TestCaseBaseForParser):
    def test_value_definition_with_relativity_that_is_not_default_relativity(self):
        instruction_argument = '--rel VALUE_DEF_NAME file-name.txt'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(
                          value_definitions=symbol_table_from_entries([
                              symbol_table.Entry('VALUE_DEF_NAME',
                                                 file_ref_value(file_refs.rel_tmp_user('value-def-path-arg')))])
                      ),
                      Expectation(
                          main_side_effects_on_files=tmp_user_dir_contains_exactly(DirContents([
                              Dir('value-def-path-arg',
                                  [empty_file('file-name.txt')])
                          ])),
                          value_definition_usages=assert_value_usages_is_singleton_list_with_value_reference(
                              ValueReferenceOfPath('VALUE_DEF_NAME',
                                                   RELATIVITY_VARIANTS)),
                      )
                      )

    def test_WHEN_no_value_reference_THEN_no_value_usages(self):
        instruction_argument = '--rel-tmp file-name.txt'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(),
                      Expectation(
                          value_definition_usages=asrt.is_empty),
                      )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
