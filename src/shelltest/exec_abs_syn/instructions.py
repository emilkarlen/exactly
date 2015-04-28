__author__ = 'emil'

import pathlib

from shelltest.execution.execution_directory_structure import ExecutionDirectoryStructure
from shelltest.phase_instr.model import InstructionExecutor
from shelltest.exec_abs_syn import script_stmt_gen


class PhaseEnvironment:
    """
    Base class for phase environments.
    """
    pass


class PhaseEnvironmentForAnonymousPhase(PhaseEnvironment):
    def __init__(self, home_dir: str):
        self.home_dir = home_dir


class PhaseEnvironmentForScriptGeneration(PhaseEnvironment):
    """
    The phase-environment for phases that generate a script.
    """

    def __init__(self,
                 script_file_management: script_stmt_gen.ScriptFileManager,
                 script_source_writer: script_stmt_gen.ScriptSourceWriter,
                 stdin_file_name: str=None):
        self.__script_file_management = script_file_management
        self.__script_source_writer = script_source_writer
        self.stdin_file_name = stdin_file_name

    # def extend_statements(self, statements_generators: list):
    # """
    # :param statements_generators: List of StatementsGeneratorForInstruction.
    # """
    # self.statements_generators.extend(statements_generators)

    def set_stdin_file(self,
                       file_name: str):
        self.stdin_file_name = file_name

    @property
    def script_file_management(self) -> script_stmt_gen.ScriptFileManager:
        return self.__script_file_management

    @property
    def append(self) -> script_stmt_gen.ScriptSourceWriter:
        return self.__script_source_writer

    @property
    def final_script_source(self) -> str:
        """
        Gives the source code for the complete script.
        """
        return self.__script_source_writer.final_source_lines()


class PhaseEnvironmentForInternalCommands(PhaseEnvironment):
    """
    The phase-environment for phases that are implemented internally
    - in Python.
    """

    def __init__(self):
        pass


class GlobalEnvironmentForNamedPhase:
    def __init__(self,
                 home_dir: pathlib.Path,
                 eds: ExecutionDirectoryStructure):
        self.__home_dir = home_dir
        self.__eds = eds

    @property
    def home_directory(self) -> pathlib.Path:
        return self.__home_dir

    @property
    def execution_directory_structure(self) -> ExecutionDirectoryStructure:
        return self.__eds

    @property
    def eds(self) -> ExecutionDirectoryStructure:
        return self.__eds


class AnonymousPhaseInstruction(InstructionExecutor):
    """
    Abstract base class for instructions of the anonymous phase.
    """
    def execute(self, phase_name: str,
                global_environment,
                phase_environment: PhaseEnvironmentForAnonymousPhase):
        """
        Does whatever this instruction should do.
        :param phase_name The phase in which this instruction is in.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class InternalInstruction(InstructionExecutor):
    """
    Abstract base class for instructions that are implemented in python.
    """
    def execute(self, phase_name: str,
                global_environment: GlobalEnvironmentForNamedPhase,
                phase_environment: PhaseEnvironmentForInternalCommands):
        """
        Does whatever this instruction should do.
        :param phase_name The phase in which this instruction is in.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class SetupPhaseInstruction(InternalInstruction):
    """
    Abstract base class for instructions of the SETUP phase.
    """
    def execute(self, phase_name: str,
                global_environment: GlobalEnvironmentForNamedPhase,
                phase_environment: PhaseEnvironmentForInternalCommands):
        """
        Does whatever this instruction should do.
        :param phase_name The phase in which this instruction is in.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class ActPhaseInstruction(InstructionExecutor):
    """
    Abstract base class for instructions of the ACT phase.
    """
    def execute(self, phase_name: str,
                global_environment: GlobalEnvironmentForNamedPhase,
                phase_environment: PhaseEnvironmentForScriptGeneration):
        """
        Does whatever this instruction should do.
        :param phase_name The phase in which this instruction is in.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class AssertPhaseInstruction(InternalInstruction):
    """
    Abstract base class for instructions of the ASSERT phase.
    """
    def execute(self, phase_name: str,
                global_environment: GlobalEnvironmentForNamedPhase,
                phase_environment: PhaseEnvironmentForInternalCommands):
        """
        Does whatever this instruction should do.
        :param phase_name The phase in which this instruction is in.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


class CleanupPhaseInstruction(InternalInstruction):
    """
    Abstract base class for instructions of the CLEANUP phase.
    """
    def execute(self, phase_name: str,
                global_environment: GlobalEnvironmentForNamedPhase,
                phase_environment: PhaseEnvironmentForInternalCommands):
        """
        Does whatever this instruction should do.
        :param phase_name The phase in which this instruction is in.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


