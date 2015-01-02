"""
Functionality for generating a Shell Script from a parsed Test Case file.
"""
__author__ = 'emil'

from shelltest.script_gen import stmt_gen
from shelltest.phase import Phase
from shelltest import phase

from shelltest.phase_instr import model as phase_instr_model


class PhaseEnvironmentForAnonymousPhase:
    def __init__(self, home_dir: str):
        self.home_dir = home_dir


class PhaseEnvironmentForNamedPhase:
    def __init__(self):
        self.statements_generators = []

    def extend_statements(self, statements_generators: list):
        """
        :param statements_generators: List of StatementsGeneratorForInstruction.
        """
        self.statements_generators.extend(statements_generators)

    def append_statement(self, statements_generator: stmt_gen.StatementsGeneratorForInstruction):
        self.statements_generators.append(statements_generator)


class GlobalEnvironmentForNamedPhase:
    def __init__(self, home_dir: str):
        self.__home_dir = home_dir

    @property
    def home_directory(self) -> str:
        return self.__home_dir


# class PhaseScriptFileGenerator(tuple):
# """
# Generator of a Script File for a fixed Phase.
# """
#
# def __new__(cls,
# phase: Phase,
#                 file_generator: statement_generator.ScriptFileGenerator):
#         return tuple.__new__(cls, (phase, file_generator))
#
#     @property
#     def phase(self) -> Phase:
#         return self[0]
#
#     @property
#     def file_generator(self) -> ScriptFileGenerator:
#         return self[1]
#
#
# class ScriptFileContentsGenerator:
#
#     def __init__(self, commands: list):
#         self.__commands = commands
#
#     @property
#     def commands(self) -> list:
#         """
#         :return list of ShellCommandGenerator
#         """
#         return self.__commands


class PhaseEnvironment:
    """
    The environment
    """
    pass


class TestCasePhase(tuple):
    def __new__(cls,
                phase: Phase,
                statements_generators: list):
        """
        :param statements_generators: List of StatementsGeneratorForInstruction.
        """
        return tuple.__new__(cls, (phase, statements_generators))

    @property
    def phase(self) -> Phase:
        return self[0]

    @property
    def statements_generators(self) -> list:
        return self[1]


class TestCase(tuple):
    def __new__(cls,
                settings: GlobalEnvironmentForNamedPhase,
                phase_list: list):
        """
        :param phase_list: List of TestCasePhase
        """
        return tuple.__new__(cls, (settings, phase_list))

    @property
    def settings(self) -> GlobalEnvironmentForNamedPhase:
        return self[0]

    @property
    def phase_list(self) -> list:
        """
        :return: List of TestCasePhase
        """
        return self[1]

    def lookup_phase(self, phase: Phase) -> TestCasePhase:
        for tcp in self.phase_list:
            if tcp.phase == phase:
                return tcp
        raise LookupError('Test Case contains no phase with name ' + phase.name)


def validate_and_generate(original_home_directory: str,
                          document: phase_instr_model.Document) -> TestCase:
    def test_case_from(global_env: GlobalEnvironmentForNamedPhase,
                       executed_phases: list) -> TestCase:
        phase_list = [TestCasePhase(Phase(phase_name), phase_env.statements_generators)
                      for phase_name, phase_env in executed_phases]
        return TestCase(global_env, phase_list)

    def execute_anonymous_phase() -> PhaseEnvironmentForAnonymousPhase:
        global_env = None
        phase_env = PhaseEnvironmentForAnonymousPhase(original_home_directory)
        phases_to_execute = [(None, phase_env)]
        document.execute(global_env, phases_to_execute)
        return phase_env

    def execute_named_phases(settings_from_anonymous_phase: PhaseEnvironmentForAnonymousPhase):
        global_env = GlobalEnvironmentForNamedPhase(settings_from_anonymous_phase.home_dir)
        phases_to_execute = [(ph.name, PhaseEnvironmentForNamedPhase())
                             for ph in phase.ALL_NAMED]
        document.execute(global_env, phases_to_execute)
        return global_env, phases_to_execute

    settings = execute_anonymous_phase()
    global_env, executed_phases = execute_named_phases(settings)
    return test_case_from(global_env, executed_phases)
