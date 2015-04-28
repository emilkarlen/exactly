"""
Functionality for generating a Shell Script from a parsed Test Case file.
"""
import pathlib
import shelltest
from shelltest.exec_abs_syn.instructions import AnonymousPhaseInstruction, SetupPhaseInstruction, ActPhaseInstruction, \
    CleanupPhaseInstruction, AssertPhaseInstruction
from shelltest.phase_instr.model import PhaseContents, new_empty_phase_contents

__author__ = 'emil'

from shelltest.exec_abs_syn import script_stmt_gen
from shelltest.exec_abs_syn import py_cmd_gen
from shelltest.exec_abs_syn import instructions
from shelltest.phases import Phase
from shelltest import phases

from shelltest.phase_instr import model as phase_instr_model


class PhaseEnvironmentForPythonCommands:
    """
    The phase-environment for phases that generate python commands.
    """

    def __init__(self, commands=None):
        if not commands:
            commands = []
        self.commands = commands

    def append_command(self, command: py_cmd_gen.PythonCommand):
        self.commands.append(command)


# class PhaseScriptFileGenerator(tuple):
# """
# Generator of a Script File for a fixed Phase.
# """
#
# def __new__(cls,
# phase: Phase,
# file_generator: statement_generator.ScriptFileGenerator):
# return tuple.__new__(cls, (phase, file_generator))
#
# @property
# def phase(self) -> Phase:
# return self[0]
#
# @property
# def file_generator(self) -> ScriptFileGenerator:
# return self[1]
#
#
# class ScriptFileContentsGenerator:
#
# def __init__(self, commands: list):
# self.__commands = commands
#
# @property
# def commands(self) -> list:
# """
#         :return list of ShellCommandGenerator
#         """
#         return self.__commands


class TestCasePhase(tuple):
    def __new__(cls,
                phase: Phase,
                phase_environment: instructions.PhaseEnvironment):
        """
        :param phase_environment: Either instructions.PhaseEnvironmentForScriptGeneration or instructions.PhaseEnvironmentForPythonCommands.
        """
        return tuple.__new__(cls, (phase, phase_environment))

    @property
    def phase(self) -> Phase:
        return self[0]

    @property
    def phase_environment(self) -> instructions.PhaseEnvironment:
        return self[1]


def new_test_case_phase_for_python_commands(phase: Phase,
                                            phase_environment: PhaseEnvironmentForPythonCommands) -> TestCasePhase:
    return TestCasePhase(phase, phase_environment)


def new_test_case_phase_for_script_statements(phase: Phase,
                                              phase_environment: instructions.PhaseEnvironmentForScriptGeneration) -> TestCasePhase:
    return TestCasePhase(phase, phase_environment)


class TestCase(tuple):
    def __new__(cls,
                settings: instructions.GlobalEnvironmentForNamedPhase,
                phase_list: list):
        """
        :param phase_list: List of TestCasePhase
        """
        return tuple.__new__(cls, (settings, phase_list))

    @property
    def settings(self) -> instructions.GlobalEnvironmentForNamedPhase:
        return self[0]

    @property
    def phase_list(self) -> list:
        """
        :rtype: list[TestCasePhase]
        """
        return self[1]

    def lookup_phase(self, phase: Phase) -> TestCasePhase:
        for tcp in self.phase_list:
            if tcp.phase == phase:
                return tcp
        raise LookupError('Test Case contains no phase with name ' + phase.name)


def validate_and_generate(original_home_directory: str,
                          document: phase_instr_model.Document) -> TestCase:
    def test_case_from(global_env: instructions.GlobalEnvironmentForNamedPhase,
                       executed_phases: list) -> TestCase:
        phase_list = [TestCasePhase(Phase(phase_name), phase_env)
                      for phase_name, phase_env in executed_phases]
        return TestCase(global_env, phase_list)

    def execute_anonymous_phase() -> instructions.PhaseEnvironmentForAnonymousPhase:
        global_env = None
        phase_env = instructions.PhaseEnvironmentForAnonymousPhase(original_home_directory)
        phases_to_execute = [(None, phase_env)]
        document.execute(global_env, phases_to_execute)
        return phase_env

    def phase_env_for(ph: Phase):
        return instructions.PhaseEnvironmentForScriptGeneration() \
            if ph == phases.ACT \
            else instructions.PhaseEnvironmentForPythonCommands()

    def execute_named_phases(settings_from_anonymous_phase: instructions.PhaseEnvironmentForAnonymousPhase):
        global_env = instructions.GlobalEnvironmentForNamedPhase(settings_from_anonymous_phase.home_dir)
        phases_to_execute = [(ph.name, phase_env_for(ph))
                             for ph in phases.ALL_NAMED]
        document.execute(global_env, phases_to_execute)
        return global_env, phases_to_execute

    settings = execute_anonymous_phase()
    global_env, executed_phases = execute_named_phases(settings)
    return test_case_from(global_env, executed_phases)


# Refaktorering


class TestCase2(tuple):
    def __new__(cls,
                anonymous_phase: PhaseContents,
                setup_phase: PhaseContents,
                act_phase: PhaseContents,
                assert_phase: PhaseContents,
                cleanup_phase: PhaseContents):
        """
        :param phase_list: List of TestCasePhase
        """
        TestCase2.__assert_instruction_class(anonymous_phase, AnonymousPhaseInstruction)
        TestCase2.__assert_instruction_class(setup_phase, SetupPhaseInstruction)
        TestCase2.__assert_instruction_class(act_phase, ActPhaseInstruction)
        TestCase2.__assert_instruction_class(assert_phase, AssertPhaseInstruction)
        TestCase2.__assert_instruction_class(cleanup_phase, CleanupPhaseInstruction)
        return tuple.__new__(cls, (anonymous_phase,
                                   setup_phase,
                                   act_phase,
                                   assert_phase,
                                   cleanup_phase))

    @property
    def anonymous_phase(self) -> PhaseContents:
        return self[0]

    @property
    def setup_phase(self) -> PhaseContents:
        return self[1]

    @property
    def act_phase(self) -> PhaseContents:
        return self[2]

    @property
    def assert_phase(self) -> PhaseContents:
        return self[3]

    @property
    def cleanup_phase(self) -> PhaseContents:
        return self[4]

    @staticmethod
    def __assert_instruction_class(phase_contents: PhaseContents,
                                   instruction_class):
        for element in phase_contents.elements:
            if element.is_instruction:
                assert isinstance(element.executor, instruction_class)


def new_test_case(document: phase_instr_model.Document) -> TestCase2:
    def get(phase_name: str) -> PhaseContents:
        try:
            phase_contents = document.instructions_for_phase(phase_name)
            return phase_contents
        except KeyError:
            return new_empty_phase_contents()

    anonymous_phase = get(shelltest.phases.ANONYMOUS.name)
    setup_phase = get(shelltest.phases.SETUP.name)
    act_phase = get(shelltest.phases.ACT.name)
    assert_phase = get(shelltest.phases.CLEANUP.name)
    cleanup_phase = get(shelltest.phases.CLEANUP.name)

    return TestCase2(anonymous_phase,
                     setup_phase,
                     act_phase,
                     assert_phase,
                     cleanup_phase)



