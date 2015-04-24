__author__ = 'emil'

import os
import pathlib
import tempfile

from shelltest.exec_abs_syn.config import Configuration
from shelltest.phase_instr import line_source
from shelltest import phases
from shelltest.exec_abs_syn import script_stmt_gen
from shelltest.execution import write_testcase_file, execution_directory_structure

import unittest


def dummy_line(line_number: int) -> line_source.Line:
    return line_source.Line(line_number,
                            str(line_number))


HOME_DIR_HEADER = 'Home Dir: '
TEST_ROOT_DIR_HEADER = 'Test Root Dir: '


class TheScriptLanguage(script_stmt_gen.ScriptLanguage):
    def base_name_from_stem(self, stem):
        return stem + '.test'

    def raw_script_statement(self, statement: str) -> list:
        return [statement]

    def comment_line(self, comment: str) -> list:
        line = '# ' + comment
        return [line]

    def comment_lines(self, lines: list) -> list:
        return ['# ' + line for line in lines]

    def source_line_header(self, source_line: line_source.Line) -> list:
        line_ref = 'Line %d' % source_line.line_number
        line_contents = source_line.text
        return self.comment_lines([line_ref,
                                   line_contents])


class StatementsGeneratorThatOutputsHomeDir(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self):
        super().__init__()

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        line = HOME_DIR_HEADER + str(configuration.home_dir)
        return script_language.raw_script_statement(line)


class StatementsGeneratorThatOutputsTestRootDir(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self):
        super().__init__()

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        line = TEST_ROOT_DIR_HEADER + str(configuration.test_root_dir)
        return script_language.raw_script_statement(line)


class Test(unittest.TestCase):
    def test_that_output_and_exitcode_are_stored(self):
        # ARRANGE #
        statement_on_line_1 = StatementsGeneratorThatOutputsHomeDir()
        statement_on_line_2 = StatementsGeneratorThatOutputsTestRootDir()
        statement_generators = [statement_on_line_1,
                                statement_on_line_2]

        script_language = TheScriptLanguage()

        with tempfile.TemporaryDirectory(prefix='shelltest-test-') as tmp_exec_dir_structure_root:
            execution_dir_structure = execution_directory_structure.construct_at(tmp_exec_dir_structure_root)

            home_path = pathlib.Path().resolve()
            configuration = Configuration(home_path,
                                          execution_dir_structure.test_root_dir)

            # ACT #
            actual_file_path = write_testcase_file.write(script_language,
                                                         execution_dir_structure,
                                                         configuration,
                                                         phases.ACT,
                                                         statement_generators)
            # ASSERT #
            expected_base_name = script_language.base_name_from_stem(phases.ACT.name)
            expected_dir = execution_dir_structure.test_case_dir
            expected_file_path = expected_dir / expected_base_name

            self.assertEqual(str(expected_file_path),
                             str(actual_file_path),
                             'Path of constructed script file')

            self.assertTrue(actual_file_path.exists(),
                            'The file should exist')

            expected_contents = os.linesep.join(['# Line 1',
                                                 '# one',
                                                 HOME_DIR_HEADER + str(home_path),
                                                 '# Line 2',
                                                 '# two',
                                                 TEST_ROOT_DIR_HEADER + str(execution_dir_structure.test_root_dir),
                                                 ''])
            self.assert_contents_is(expected_contents,
                                    actual_file_path)

    def assert_contents_is(self,
                           expected_contents: str,
                           actual_file_path: pathlib.Path):
        f = open(str(actual_file_path))
        actual_contents = f.read()
        f.close()
        self.assertEqual(expected_contents,
                         actual_contents,
                         'Contents')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(Test))
    return ret_val


if __name__ == '__main__':
    unittest.main()
