__author__ = 'emil'

import unittest

from shelltest.phase_instr import line_source
from shelltest.script_gen import abs_syn_gen
from shelltest.phase_instr import model as phase_instr_model
from shelltest import phase
from shelltest.script_gen import stmt_gen


def dummy_line(line_number: int) -> line_source.Line:
    return line_source.Line(line_number,
                            str(line_number))


class StatementsGeneratorThatStoresHomeDir(stmt_gen.StatementsGeneratorForInstruction):
    def __init__(self,
                 source_line: line_source.Line,
                 home_dir: str):
        super().__init__(source_line)
        self.home_dir = home_dir

    def instruction_implementation(self,
                                   configuration: stmt_gen.Configuration,
                                   statement_constructor: stmt_gen.ScriptLanguageStatementConstructor) -> list:
        raise NotImplementedError()


class InstructionThatSetsHomeDir(phase_instr_model.Instruction):
    def __init__(self,
                 line_number: int,
                 home_dir_to_set: str):
        super().__init__(dummy_line(line_number))
        self.__home_dir_to_set = home_dir_to_set

    def execute(self,
                phase_name: str,
                global_environment,
                phase_environment: abs_syn_gen.PhaseEnvironmentForAnonymousPhase):
        phase_environment.home_dir = self.__home_dir_to_set


class InstructionThatRecordsHomeDir(phase_instr_model.Instruction):
    def __init__(self,
                 line_number: int):
        super().__init__(dummy_line(line_number))

    def execute(self,
                phase_name: str,
                global_environment: abs_syn_gen.GlobalEnvironmentForNamedPhase,
                phase_environment: abs_syn_gen.PhaseEnvironmentForNamedPhase):
        phase_environment.append_statement(StatementsGeneratorThatStoresHomeDir(self.source_line,
                                                                                global_environment.home_directory))


class TestGenerate(unittest.TestCase):

    def test_gen(self):
        # ARRANGE #
        phase2instructions = {
            phase.ANONYMOUS.name: phase_instr_model.InstructionSequence(
                (InstructionThatSetsHomeDir(1,
                                            'updated-home-dir'),)),
            phase.APPLY.name: phase_instr_model.InstructionSequence(
                (InstructionThatRecordsHomeDir(2),)),
        }
        document = phase_instr_model.Document(phase2instructions)
        # ACT #
        test_case = abs_syn_gen.validate_and_generate('original-home-dir',
                                                      document)

        # ASSERT #
        self.assertEqual('updated-home-dir',
                         test_case.settings.home_directory,
                         'Home directory should have been updated')

        test_case_phase_for_apply = test_case.lookup_phase(phase.APPLY)

        self.assertEqual('updated-home-dir',
                         test_case.settings.home_directory,
                         'Home directory in the environment should have been updated')
        self.assertEqual(1,
                         len(test_case_phase_for_apply.statements_generators),
                         'Number of generators')
        the_generator = test_case_phase_for_apply.statements_generators[0]
        self.assertIsInstance(the_generator, StatementsGeneratorThatStoresHomeDir)
        self.assertEqual('updated-home-dir', the_generator.home_dir,
                         'The generator should have recorded the updated home-dir')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestGenerate))
    return ret_val


if __name__ == '__main__':
    unittest.main()
