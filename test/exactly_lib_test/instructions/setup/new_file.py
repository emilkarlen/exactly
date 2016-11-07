import unittest

from exactly_lib.instructions.setup import new_file as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check
from exactly_lib_test.test_resources.execution.sds_contents_check__va import act_dir_contains_exactly
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, Dir, empty_file, File
from exactly_lib_test.test_resources.parse import new_source2, argument_list_source


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TestCasesThatTestIntegrationByAFewRandomTests(TestCaseBaseForParser):
    def test_file_in_sub_dir__sub_dir_exists(self):
        self._run(new_source2('existing-directory/file-name.txt'),
                  Arrangement(eds_contents_before_main=act_dir_contents(DirContents([
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
                  ])))
                  )

    def test_argument_is_existing_file(self):
        self._run(new_source2('existing-file'),
                  Arrangement(eds_contents_before_main=act_dir_contents(DirContents([
                      empty_file('existing-file')
                  ]))),
                  Expectation(main_result=sh_check.is_hard_error())
                  )


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationByAFewRandomTests))
    return ret_val

if __name__ == '__main__':
    unittest.main()
