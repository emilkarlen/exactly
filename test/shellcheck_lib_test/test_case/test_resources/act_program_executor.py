import pathlib
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
        self.program_executor.execute(self.source_setup,
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
                             process_result.stdout)

    def test_stderr_is_connected_to_program(self):
        program = self.test_setup.program_that_prints_to_stderr('expected output on stderr')
        process_result = self.__execute(program)
        self.put.assertEqual('expected output on stderr',
                             process_result.stderr)

    def test_stdin_and_stdout_are_connected_to_program(self):
        program = self.test_setup.program_that_copes_stdin_to_stdout()
        process_result = self.__execute(program,
                                        stdin_contents='contents of stdin')
        self.put.assertEqual('contents of stdin',
                             process_result.stdout)

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
