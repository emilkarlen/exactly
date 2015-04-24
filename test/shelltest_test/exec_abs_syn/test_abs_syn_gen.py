__author__ = 'emil'

import unittest

from shelltest.exec_abs_syn.config import Configuration
from shelltest.phase_instr import line_source
from shelltest.exec_abs_syn import abs_syn_gen
from shelltest.phase_instr import model as phase_instr_model
from shelltest import phases
from shelltest.exec_abs_syn import script_stmt_gen
from shelltest.exec_abs_syn import py_cmd_gen


def dummy_line(line_number: int) -> line_source.Line:
    return line_source.Line(line_number,
                            str(line_number))


class StatementsGeneratorThatStoresHomeDir(script_stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self,
                 home_dir: str):
        super().__init__()
        self.home_dir = home_dir

    def instruction_implementation(self,
                                   configuration: Configuration,
                                   script_language: script_stmt_gen.ScriptLanguage) -> list:
        raise RuntimeError('Should not be called')


class PythonCommandThatStoresHomeDir(py_cmd_gen.PythonCommand):
    def __init__(self,
                 home_dir: str):
        super().__init__()
        self.home_dir = home_dir

    def apply(self, configuration: Configuration):
        raise RuntimeError('Should not be called')


def instruction(line_number: int,
                executor: phase_instr_model.InstructionExecutor) -> phase_instr_model.PhaseContentElement:
    return phase_instr_model.new_instruction_element(
        dummy_line(line_number),
        executor)


class InstructionThatSetsHomeDir(phase_instr_model.InstructionExecutor):
    def __init__(self,
                 home_dir_to_set: str):
        self.__home_dir_to_set = home_dir_to_set

    def execute(self,
                phase_name: str,
                global_environment,
                phase_environment: abs_syn_gen.PhaseEnvironmentForAnonymousPhase):
        phase_environment.home_dir = self.__home_dir_to_set


class InstructionThatRecordsHomeDirAsScriptStatement(phase_instr_model.InstructionExecutor):
    def execute(self,
                phase_name: str,
                global_environment: abs_syn_gen.GlobalEnvironmentForNamedPhase,
                phase_environment: abs_syn_gen.PhaseEnvironmentForScriptGeneration):
        phase_environment.append_statement(StatementsGeneratorThatStoresHomeDir(global_environment.home_directory))


class InstructionThatRecordsHomeDirAsPythonCommand(phase_instr_model.InstructionExecutor):
    def execute(self,
                phase_name: str,
                global_environment: abs_syn_gen.GlobalEnvironmentForNamedPhase,
                phase_environment: abs_syn_gen.PhaseEnvironmentForPythonCommands):
        phase_environment.append_command(PythonCommandThatStoresHomeDir(global_environment.home_directory))


class TestGenerate(unittest.TestCase):
    def test_gen(self):
        # ARRANGE #
        phase2instructions = {
            phases.ANONYMOUS.name: phase_instr_model.PhaseContents(
                (instruction(1,
                             InstructionThatSetsHomeDir('updated-home-dir')),)),
            phases.SETUP.name: phase_instr_model.PhaseContents(
                (instruction(2,
                 InstructionThatRecordsHomeDirAsPythonCommand()),)),
            phases.ACT.name: phase_instr_model.PhaseContents(
                (instruction(3,
                             InstructionThatRecordsHomeDirAsScriptStatement()),)),
            phases.ASSERT.name: phase_instr_model.PhaseContents(
                (instruction(4,
                             InstructionThatRecordsHomeDirAsPythonCommand()),)),
            phases.CLEANUP.name: phase_instr_model.PhaseContents(
                (instruction(5,
                             InstructionThatRecordsHomeDirAsPythonCommand()),)),
        }
        document = phase_instr_model.Document(phase2instructions)
        # ACT #
        test_case = abs_syn_gen.validate_and_generate('original-home-dir',
                                                      document)

        # ASSERT #
        self.assertEqual('updated-home-dir',
                         test_case.settings.home_directory,
                         'Home directory should have been updated')

        self.assert_has_single_script_statements_generator_that_stores_home_dir(
            'updated-home-dir',
            test_case.lookup_phase(phases.ACT).phase_environment)

        self.assert_has_single_py_command_that_stores_home_dir('updated-home-dir',
                                                               test_case.lookup_phase(phases.SETUP).phase_environment)
        self.assert_has_single_py_command_that_stores_home_dir('updated-home-dir',
                                                               test_case.lookup_phase(phases.ASSERT).phase_environment)
        self.assert_has_single_py_command_that_stores_home_dir('updated-home-dir',
                                                               test_case.lookup_phase(phases.CLEANUP).phase_environment)

    def assert_has_single_py_command_that_stores_home_dir(self,
                                                          expected_home_dir: str,
                                                          phase_environment):
        self.assertIsInstance(phase_environment,
                              abs_syn_gen.PhaseEnvironmentForPythonCommands)
        self.assertEqual(1,
                         len(phase_environment.commands),
                         'Number of generators')
        the_command = phase_environment.commands[0]
        self.assertIsInstance(the_command, PythonCommandThatStoresHomeDir)
        self.assertEqual(expected_home_dir, the_command.home_dir,
                         'The generator should have recorded the updated home-dir')

    def assert_has_single_script_statements_generator_that_stores_home_dir(self,
                                                                           expected_home_dir: str,
                                                                           phase_environment):
        self.assertIsInstance(phase_environment,
                              abs_syn_gen.PhaseEnvironmentForScriptGeneration)
        self.assertEqual(1,
                         len(phase_environment.statements_generators),
                         'Number of generators')
        the_generator = phase_environment.statements_generators[0]
        self.assertIsInstance(the_generator, StatementsGeneratorThatStoresHomeDir)
        self.assertEqual(expected_home_dir, the_generator.home_dir,
                         'The generator should have recorded the updated home-dir')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestGenerate))
    return ret_val


if __name__ == '__main__':
    unittest.main()
