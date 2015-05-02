from shelltest.exec_abs_syn.instruction_result import new_success
from shelltest.exec_abs_syn.instructions import SuccessOrHardError

__author__ = 'emil'

import os
import shutil
import pathlib
import unittest

from shelltest import phases
from shelltest.exec_abs_syn import instructions
from shelltest.execution.execution_directory_structure import ExecutionDirectoryStructure
from shelltest.phase_instr import model
from shelltest.phase_instr import line_source
from shelltest.script_language import python3
from shelltest.exec_abs_syn import abs_syn_gen
from shelltest.execution import execution
from shelltest_test.execution.util import utils, instruction_adapter


ANONYMOUS = 'anonymous'
SETUP = phases.SETUP.name
ACT_SCRIPT_GENERATION = phases.ACT.name + '/script-generation'
ACT_SCRIPT_EXECUTION = phases.ACT.name + '/script-execution'
ASSERT = phases.ASSERT.name
CLEANUP = phases.CLEANUP.name


class ListRecorder:
    def __init__(self,
                 recorder: list,
                 element: str):
        self.recorder = recorder
        self.element = element

    def record(self):
        self.recorder.append(self.element)


class TestCaseThatRecordsExecution:
    """
    Base class for tests on a test case that uses the Python 3 language in the apply phase.
    """

    def __init__(self,
                 unittest_case: unittest.TestCase,
                 expected_internal_recording: list,
                 expected_file_recording: list,
                 execution_directory_structure_should_exist: bool,
                 dbg_do_not_delete_dir_structure=False):
        self.__previous_line_number = 0
        self.__unittest_case = unittest_case
        self.__dbg_do_not_delete_dir_structure = dbg_do_not_delete_dir_structure
        self.__expected_internal_recording = expected_internal_recording
        self.__expected_file_recording = expected_file_recording
        self.__execution_directory_structure_should_exist = execution_directory_structure_should_exist

        self.__recorder = []
        self.__full_result = None
        self.__execution_directory_structure = None

    def execute(self):
        # ARRANGE #
        home_dir_path = pathlib.Path().resolve()
        test_case = self._test_case()
        # ACT #
        full_result = execution.execute(
            python3.Python3ScriptFileManager(),
            python3.new_script_source_writer(),
            test_case,
            home_dir_path,
            'shelltest-test-',
            True)

        # ASSERT #
        self.__full_result = full_result
        self._assertions()
        # CLEANUP #
        os.chdir(str(home_dir_path))
        if not self.__dbg_do_not_delete_dir_structure and self.eds:
            shutil.rmtree(str(self.eds.root_dir))
        else:
            if self.eds:
                print(str(self.eds.root_dir))

    def _next_line(self) -> line_source.Line:
        """
        Generates lines in a continuous sequence.
        """
        self.__previous_line_number += 1
        return line_source.Line(self.__previous_line_number,
                                str(self.__previous_line_number))

    def _next_instruction_line(self, instruction: model.Instruction) -> model.PhaseContentElement:
        return model.new_instruction_element(
            self._next_line(),
            instruction)

    def _assertions(self):
        self.unittest_case.assertEqual(self.__expected_internal_recording,
                                       self.__recorder)
        if self.__execution_directory_structure_should_exist:
            self.__unittest_case.assertIsNotNone(self.eds)
            self.__unittest_case.assertTrue(self.eds.root_dir.is_dir())
            file_path = record_file_path(self.eds)
            if not self.__expected_file_recording:
                self.__unittest_case.assertFalse(file_path.exists())
            else:
                expected_file_contents = record_file_contents_from_lines(self.__expected_file_recording)
                self.assert_is_regular_file_with_contents(file_path,
                                                          expected_file_contents)
        else:
            self.__unittest_case.assertIsNone(self.eds)



    @property
    def unittest_case(self) -> unittest.TestCase:
        return self.__unittest_case

    @property
    def eds(self) -> execution.ExecutionDirectoryStructure:
        return self.__full_result.execution_directory_structure

    def assert_is_regular_file_with_contents(self,
                                             path: pathlib.Path,
                                             expected_contents: str):
        """
        Helper for test cases that check the contents of files.
        """
        utils.assert_is_file_with_contents(self.unittest_case,
                                           path,
                                           expected_contents)

    def _test_case(self) -> abs_syn_gen.TestCase:
        return abs_syn_gen.TestCase(
            self.__from(self._anonymous_phase_recording(phases.ANONYMOUS) +
                        self._anonymous_phase_extra()),
            self.__from(self._setup_phase_recording(phases.SETUP) +
                        self._setup_phase_extra()),
            self.__from(self._act_phase_recording() +
                        self._act_phase_extra()),
            self.__from(self._assert_phase_recording(phases.ASSERT) +
                        self._assert_phase_extra()),
            self.__from(self._cleanup_phase_recording(phases.CLEANUP) +
                        self._cleanup_phase_extra())
        )

    def __from(self,
               instruction_list: list) -> model.PhaseContents:
        elements = [self._next_instruction_line(instr)
                    for instr in instruction_list]
        return model.PhaseContents(tuple(elements))

    def _anonymous_phase_recording(self,
                                   phase: phases.Phase) -> list:
        return [
            AnonymousInternalInstructionThatRecordsStringInList(self.__recorder_of(phase.name))
        ]

    def _anonymous_phase_extra(self) -> list:
        return []

    def _setup_phase_recording(self,
                               phase: phases.Phase) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type SetupPhaseInstruction)
        """
        return [
            instruction_adapter.as_setup(InternalInstructionThatRecordsStringInList(self.__recorder_of(phase.name))),
            instruction_adapter.as_setup(InternalInstructionThatRecordsStringInRecordFile(phase.name)),
        ]

    def _setup_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type SetupPhaseInstruction)
        """
        return []

    def _act_phase_recording(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type ActPhaseInstruction)
        """
        return [
            ActInstructionThatRecordsStringInList(self.__recorder_of(ACT_SCRIPT_GENERATION)),
            ActInstructionThatRecordsStringInRecordFile(ACT_SCRIPT_EXECUTION),
        ]

    def _act_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type ActPhaseInstruction)
        """
        return []

    def _assert_phase_recording(self,
                                phase: phases.Phase) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AssertPhaseInstruction)
        """
        return [
            instruction_adapter.as_assert(InternalInstructionThatRecordsStringInList(self.__recorder_of(phase.name))),
            instruction_adapter.as_assert(InternalInstructionThatRecordsStringInRecordFile(phase.name)),
        ]

    def _assert_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type AssertPhaseInstruction)
        """
        return []

    def _cleanup_phase_recording(self,
                                 phase: phases.Phase) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type CleanupPhaseInstruction)
        """
        return [
            instruction_adapter.as_cleanup(InternalInstructionThatRecordsStringInList(self.__recorder_of(phase.name))),
            instruction_adapter.as_cleanup(InternalInstructionThatRecordsStringInRecordFile(phase.name)),
        ]

    def _cleanup_phase_extra(self) -> list:
        """
        :rtype list[PhaseContentElement] (with instruction of type CleanupPhaseInstruction)
        """
        return []

    def __recorder_of(self, s: str) -> ListRecorder:
        return ListRecorder(self.__recorder,
                            s)


class TestCaseThatRecordsExecutionWithSingleExtraInstruction(TestCaseThatRecordsExecution):
    def __init__(self,
                 unittest_case: unittest.TestCase,
                 expected_internal_recording: list,
                 expected_file_recording: list,
                 execution_directory_structure_should_exist: bool,
                 anonymous_extra: instructions.AnonymousPhaseInstruction,
                 setup_extra: instructions.SetupPhaseInstruction,
                 act_extra: instructions.ActPhaseInstruction,
                 assert_extra: instructions.AssertPhaseInstruction,
                 cleanup_extra: instructions.CleanupPhaseInstruction,
                 dbg_do_not_delete_dir_structure=False):
        super().__init__(unittest_case,
                         expected_internal_recording,
                         expected_file_recording,
                         execution_directory_structure_should_exist,
                         dbg_do_not_delete_dir_structure)
        self.__anonymous_extra = anonymous_extra
        self.__setup_extra = setup_extra
        self.__act_extra = act_extra
        self.__assert_extra = assert_extra
        self.__cleanup_extra = cleanup_extra

    def _anonymous_phase_extra(self) -> list:
        return [self.__anonymous_extra] if self.__anonymous_extra else []

    def _setup_phase_extra(self) -> list:
        return [self.__setup_extra] if self.__setup_extra else []

    def _act_phase_extra(self) -> list:
        return [self.__act_extra] if self.__act_extra else []

    def _assert_phase_extra(self) -> list:
        return [self.__assert_extra] if self.__assert_extra else []

    def _cleanup_phase_extra(self) -> list:
        return [self.__cleanup_extra] if self.__cleanup_extra else []


class InternalInstructionThatRecordsStringInRecordFile(instructions.InternalInstruction):
    def __init__(self, s: str):
        self.__s = s

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        append_line_to_record_file(global_environment.execution_directory_structure,
                                   self.__s)


class InternalInstructionThatRecordsStringInList(instructions.InternalInstruction):
    def __init__(self,
                 recorder: ListRecorder):
        self.__recorder = recorder

    def execute(self, phase_name: str,
                global_environment: instructions.GlobalEnvironmentForNamedPhase,
                phase_environment: instructions.PhaseEnvironmentForInternalCommands):
        self.__recorder.record()


class ActInstructionThatRecordsStringInRecordFile(instructions.ActPhaseInstruction):
    def __init__(self, s: str):
        self.__s = s

    def update_phase_environment(self, phase_name: str,
                                 global_environment: instructions.GlobalEnvironmentForNamedPhase,
                                 phase_environment: instructions.PhaseEnvironmentForScriptGeneration):
        phase_environment.append.raw_script_statements(
            append_line_to_record_file_statements(global_environment.execution_directory_structure,
                                                  self.__s))


class ActInstructionThatRecordsStringInList(instructions.ActPhaseInstruction):
    def __init__(self,
                 recorder: ListRecorder):
        self.__recorder = recorder

    def update_phase_environment(self, phase_name: str,
                                 global_environment: instructions.GlobalEnvironmentForNamedPhase,
                                 phase_environment: instructions.PhaseEnvironmentForScriptGeneration):
        self.__recorder.record()


class AnonymousInternalInstructionThatRecordsStringInList(instructions.AnonymousPhaseInstruction):
    def __init__(self,
                 recorder: ListRecorder):
        self.__recorder = recorder

    def execute(self, phase_name: str,
                global_environment,
                phase_environment: instructions.PhaseEnvironmentForAnonymousPhase) -> SuccessOrHardError:
        self.__recorder.record()
        return new_success()


RECORD_FILE_BASE_NAME = 'recording.txt'


def record_file_path(eds: ExecutionDirectoryStructure) -> pathlib.Path:
    return eds.root_dir / RECORD_FILE_BASE_NAME


def record_file_contents_from_lines(lines: list) -> str:
    return '\n'.join(lines) + '\n'


def append_line_to_record_file(eds: ExecutionDirectoryStructure,
                               line: str):
    append_line_to_file(record_file_path(eds), line)


def append_line_to_record_file_statements(eds: ExecutionDirectoryStructure,
                                          line: str) -> list:
    return [
        'with open(\'%s\', \'a\') as f:' % (str(record_file_path(eds))),
        '  f.write(\'%s\')' % (line + '\\n'),
    ]


def append_line_to_file(file_path: pathlib.Path,
                        line: str):
    with open(str(file_path), 'a') as f:
        f.write(line + '\n')
