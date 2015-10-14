import os
import pathlib
import random
import unittest

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.general.output import StdFiles
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.act.phase_setup import ActProgramExecutor, SourceSetup
from shellcheck_lib_test.util.with_tmp_file import ProcessExecutor, SubProcessResult
from shellcheck_lib_test.instructions.utils import execution_directory_structure
from shellcheck_lib_test.util.with_tmp_file import capture_process_executor_result


class ActProgramExecutorTestSetup:
    def __init__(self, sut: ActProgramExecutor):
        self.sut = sut

    def program_that_copes_stdin_to_stdout(self) -> ScriptSourceBuilder:
        raise NotImplementedError()

    def program_that_prints_to_stdout(self, string_to_print: str) -> ScriptSourceBuilder:
        raise NotImplementedError()

    def program_that_prints_to_stderr(self, string_to_print: str) -> ScriptSourceBuilder:
        raise NotImplementedError()

    def program_that_exits_with_code(self, exit_code: int) -> ScriptSourceBuilder:
        raise NotImplementedError()

    def program_that_prints_cwd_without_new_line_to_stdout(self) -> ScriptSourceBuilder:
        raise NotImplementedError()

    def program_that_prints_value_of_environment_variable_to_stdout(self, var_name: str) -> ScriptSourceBuilder:
        raise NotImplementedError()


class _ProcessExecutorForProgramExecutor(ProcessExecutor):
    def __init__(self,
                 source_setup: SourceSetup,
                 eds: ExecutionDirectoryStructure,
                 program_executor: ActProgramExecutor):
        self.program_executor = program_executor
        self.source_setup = source_setup
        self.eds = eds

    def execute(self,
                cwd: str,
                files: StdFiles) -> int:
        return self.program_executor.execute(self.source_setup,
                                             pathlib.Path(cwd),
                                             self.eds,
                                             files.stdin,
                                             files.output)


class Tests:
    def __init__(self,
                 put: unittest.TestCase,
                 test_setup: ActProgramExecutorTestSetup):
        self.put = put
        self.test_setup = test_setup

    def test_stdout_is_connected_to_program(self):
        program = self.test_setup.program_that_prints_to_stdout('expected output on stdout')
        process_result = self.__execute(program)
        self.put.assertEqual('expected output on stdout',
                             process_result.stdout,
                             'Contents of stdout')

    def test_stderr_is_connected_to_program(self):
        program = self.test_setup.program_that_prints_to_stderr('expected output on stderr')
        process_result = self.__execute(program)
        self.put.assertEqual('expected output on stderr',
                             process_result.stderr,
                             'Contents of stderr')

    def test_stdin_and_stdout_are_connected_to_program(self):
        program = self.test_setup.program_that_copes_stdin_to_stdout()
        process_result = self.__execute(program,
                                        stdin_contents='contents of stdin')
        self.put.assertEqual('contents of stdin',
                             process_result.stdout,
                             'Contents of stdout is expected to be equal to stdin')

    def test_exit_code_is_returned(self):
        program = self.test_setup.program_that_exits_with_code(87)
        process_result = self.__execute(program)
        self.put.assertEqual(87,
                             process_result.exitcode,
                             'Exit Code')

    def test_environment_variables_are_accessible_by_program(self):
        var_name = 'SHELLCHECK_TEST_VAR'
        var_value = str(random.getrandbits(32))
        os.environ[var_name] = var_value
        program = self.test_setup.program_that_prints_value_of_environment_variable_to_stdout(var_name)
        process_result = self.__execute(program)
        self.put.assertEqual(var_value,
                             process_result.stdout,
                             'Contents of stdout should be value of environment variable')

    def test_initial_cwd_is_act_directory_and_that_cwd_is_restored_afterwards(self):
        cwd_before = os.getcwd()
        source = self.test_setup.program_that_prints_cwd_without_new_line_to_stdout()
        act_program_executor = self.test_setup.sut
        validation_result = act_program_executor.validate(source)
        self.put.assertEqual(svh.new_svh_success(),
                             validation_result)
        with execution_directory_structure() as eds:
            program_setup = SourceSetup(source,
                                        eds.test_case_dir,
                                        'file-name-stem')
            act_program_executor.prepare(program_setup, eds)
            process_executor = _ProcessExecutorForProgramExecutor(program_setup,
                                                                  eds,
                                                                  act_program_executor)
            process_result = capture_process_executor_result(process_executor,
                                                             eds.result.root_dir,
                                                             cwd=eds.act_dir)
        self.put.assertEqual(str(eds.act_dir),
                             process_result.stdout,
                             'Current Working Directory for program should be act-directory')

        self.put.assertEqual(cwd_before,
                             os.getcwd(),
                             'Current Working Directory should be restored after program has finished')

    def __execute(self,
                  source: ScriptSourceBuilder,
                  stdin_contents: str='') -> SubProcessResult:
        act_program_executor = self.test_setup.sut
        validation_result = act_program_executor.validate(source)
        self.put.assertEqual(svh.new_svh_success(),
                             validation_result)
        with execution_directory_structure() as eds:
            program_setup = SourceSetup(source,
                                        eds.test_case_dir,
                                        'file-name-stem')
            act_program_executor.prepare(program_setup, eds)
            process_executor = _ProcessExecutorForProgramExecutor(program_setup,
                                                                  eds,
                                                                  act_program_executor)
            return capture_process_executor_result(process_executor,
                                                   eds.result.root_dir,
                                                   cwd=eds.act_dir,
                                                   stdin_contents=stdin_contents)
