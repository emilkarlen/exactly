__author__ = 'emil'

import os
import pathlib
import tempfile
import unittest

from shelltest.exec_abs_syn.config import Configuration
from shelltest.phase_instr import line_source
from shelltest import phase
from shelltest.exec_abs_syn import script_stmt_gen
from shelltest import execution_directory_structure
from shelltest.script_gen import write_testcase_file


def dummy_line(line_number: int) -> line_source.Line:
    return line_source.Line(line_number,
                            str(line_number))


class TheScriptLanguage(script_stmt_gen.ScriptLanguage):
    def base_name_from_stem(self, name):
        return name + '.test'

    def raw_script_statement(self, statement: str) -> list:
        return [statement]

    def comment_line(self, comment: str) -> list:
        line = '# ' + comment
        return [line]

    def comment_lines(self, lines: list) -> list:
        return ['# ' + line for line in lines]

    def source_line_info(self, source_line: line_source.Line) -> list:
        line_ref = 'Line %d' % source_line.line_number
        line_contents = source_line.text
        return self.comment_lines([line_ref,
                                   line_contents])


class StatementsGeneratorForSingleRawScriptStatement(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self,
                 source_line: line_source.Line,
                 raw_script_statement: str):
        super().__init__(source_line)
        self.raw_script_statement = raw_script_statement

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        return script_language.raw_script_statement(self.raw_script_statement)


class StatementsGeneratorThatOutputsHomeDir(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self,
                 source_line: line_source.Line):
        super().__init__(source_line)

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        return script_language.raw_script_statement(str(configuration.home_dir))


class StatementsGeneratorThatOutputsTestRootDir(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self,
                 source_line: line_source.Line):
        super().__init__(source_line)

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        return script_language.raw_script_statement(str(configuration.test_root_dir))


class TestScriptGen(unittest.TestCase):
    def test_that_output_and_exitcode_are_stored(self):
        with tempfile.TemporaryDirectory(prefix='shelltest-test-') as tmp_exec_dir_structure_root:
            # ARRANGE #
            statement_on_line_1 = StatementsGeneratorThatOutputsHomeDir(line_source.Line(1, 'one'))
            statement_on_line_2 = StatementsGeneratorThatOutputsTestRootDir(line_source.Line(2, 'two'))
            statement_generators = [statement_on_line_1,
                                    statement_on_line_2]

            execution_dir_structure = execution_directory_structure.construct_at(tmp_exec_dir_structure_root)

            home_path = pathlib.Path().resolve()
            configuration = Configuration(home_path,
                                          execution_dir_structure.test_root_dir)

            script_language = TheScriptLanguage()
            # ACT #
            actual_file_path = write_testcase_file.write(script_language,
                                                         execution_dir_structure,
                                                         configuration,
                                                         phase.APPLY,
                                                         statement_generators)
            # ASSERT #
            expected_base_name = script_language.base_name_from_stem(phase.APPLY.name)
            expected_dir = execution_dir_structure.test_case_dir
            expected_file_path = expected_dir / expected_base_name

            self.assertEqual(str(expected_file_path),
                             str(actual_file_path),
                             'Path of constructed script file')

            self.assertTrue(actual_file_path.exists(),
                            'The file should exist')

            expected_contents = os.linesep.join(['# Line 1',
                                                 '# one',
                                                 str(home_path),
                                                 '# Line 2',
                                                 '# two',
                                                 str(execution_dir_structure.test_root_dir),
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
    # ret_val.addTest(test_model.suite())
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
