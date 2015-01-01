__author__ = 'emil'

import unittest

from shelltest import model


class GlobalEnvironment:
    """
    Maintains a list of executed instructions: (phase-name, instruction-name)
    """

    def __init__(self):
        self.instruction_list = []


class PhaseEnvironment:
    """
    Maintains a list of executed instructions: (phase-name, instruction-name)
    """

    def __init__(self):
        self.instruction_list = []


class InstructionThatAppendsNameToEnvironments(model.Instruction):
    def __init__(self, name: str):
        super().__init__(None)
        self.__name = name

    def execute(self, phase_name: str,
                global_environment: GlobalEnvironment,
                phase_environment: PhaseEnvironment):
        global_environment.instruction_list.append((phase_name, self.__name))
        phase_environment.instruction_list.append((phase_name, self.__name))


def instr(name: str) -> InstructionThatAppendsNameToEnvironments:
    return InstructionThatAppendsNameToEnvironments(name)


class TestDocument(unittest.TestCase):
    def test_instructions_should_be_executed_in_the_order_they_appear_in_the_sequence(self):
        phase2instructions = {
            'phase': model.InstructionSequence((instr('1'),
                                                instr('2')))
        }
        document = model.Document(phase2instructions)
        global_environment = GlobalEnvironment()
        phase_environment = PhaseEnvironment()
        phases = [('phase', phase_environment)]
        document.execute(global_environment,
                         phases)
        expected = [('phase', '1'),
                    ('phase', '2')]
        self.assertEqual(expected, global_environment.instruction_list, 'Global execution trace')
        self.assertEqual(expected, phase_environment.instruction_list, 'Phase execution trace')

    def test_phases_should_be_executed_in_the_order_they_appear_in_the_sequence(self):
        phase2instructions = {
            'a': model.InstructionSequence((instr('1'),
                                            instr('2'))),
            'b': model.InstructionSequence((instr('1'),
                                            instr('2')))
        }
        document = model.Document(phase2instructions)
        global_environment = GlobalEnvironment()
        phase_a_environment = PhaseEnvironment()
        phase_b_environment = PhaseEnvironment()
        phases = [
            ('b', phase_b_environment),
            ('a', phase_a_environment)
        ]
        document.execute(global_environment,
                         phases)
        expected_a = [
            ('a', '1'),
            ('a', '2'),
        ]
        expected_b = [
            ('b', '1'),
            ('b', '2'),
        ]
        expected_global = expected_b + expected_a

        self.assertEqual(expected_global, global_environment.instruction_list, 'Global execution trace')
        self.assertEqual(expected_a, phase_a_environment.instruction_list, 'Phase a execution trace')
        self.assertEqual(expected_b, phase_b_environment.instruction_list, 'Phase b execution trace')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestDocument))
    return ret_val


if __name__ == '__main__':
    unittest.main()
