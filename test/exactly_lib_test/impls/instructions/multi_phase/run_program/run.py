import os
import unittest
from typing import Sequence

from exactly_lib.impls.instructions.multi_phase import run as sut
from exactly_lib.impls.instructions.multi_phase.utils.instruction_from_parts_for_executing_program import \
    TheInstructionEmbryo, ExecutionResultAndStderr
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.impls.types.program import syntax_elements
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.tcfs.path_relativity import RelSdsOptionType, RelOptionType
from exactly_lib.test_case.path_resolving_env import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line_2
from exactly_lib_test.impls.types.program.test_resources import arguments_building as pgm_args, result_assertions
from exactly_lib_test.impls.types.test_resources import arguments_building as args
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.tcfs.test_resources import path_arguments
from exactly_lib_test.tcfs.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.tcfs.test_resources.sds_populator import contents_in
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_case.test_resources.instruction_settings import optionally_from_proc_exe_settings
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.programs.py_programs import py_pgm_that_exits_with_1st_value_on_command_line
from exactly_lib_test.test_resources.tcds_and_symbols import tcds_test
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestExecuteProgramWithShellArgumentList),
        unittest.makeSuite(TestExecuteInterpret),
        unittest.makeSuite(TestSource),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name',
                                                                            'single line description',
                                                                            _get_outcome)),
    ])


def _get_outcome() -> Sequence[ParagraphItem]:
    return ()


class ExecuteAction(TcdsAction):
    def __init__(self, instruction_embryo: TheInstructionEmbryo):
        self.instruction_embryo = instruction_embryo

    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds) -> ExecutionResultAndStderr:
        environment_builder = InstructionEnvironmentPostSdsBuilder.new_tcds(
            environment.tcds,
            process_execution_settings=ProcessExecutionSettings.with_environ(os.environ),
        )
        env__post_sds = environment_builder.build_post_sds()
        settings = optionally_from_proc_exe_settings(None, env__post_sds.proc_exe_settings)
        return self.instruction_embryo.main(
            env__post_sds,
            settings,
            os_services_access.new_for_current_os(),
        )


class TestCaseBase(tcds_test.TestCaseBase):
    def _check_single_line_arguments_with_source_variants(self,
                                                          instruction_argument: str,
                                                          arrangement: tcds_test.Arrangement,
                                                          expectation: tcds_test.Expectation):
        for source_case in equivalent_source_variants__with_source_check__consume_last_line_2(
                instruction_argument):
            with self.subTest(source=source_case.source.source_string):
                embryo_parser = sut.embryo_parser('instruction-name')
                instruction_embryo = embryo_parser.parse(ARBITRARY_FS_LOCATION_INFO, source_case.source)
                source_case.expectation.apply_with_message(self, source_case.source, 'source')
                action = ExecuteAction(instruction_embryo)
                self._check(action, arrangement, expectation)

    def _check_source(self,
                      source: ParseSource,
                      arrangement: tcds_test.Arrangement,
                      expectation: tcds_test.Expectation):
        parser = sut.embryo_parser('instruction-name')
        instruction_embryo = parser.parse(source)
        action = ExecuteAction(instruction_embryo)
        self._check(action, arrangement, expectation)


class TestExecuteProgramWithShellArgumentList(TestCaseBase):
    def test_check_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            pgm_args.interpret_py_source_line('exit(0)').as_str,
            tcds_test.Arrangement(),
            tcds_test.Expectation(expected_action_result=result_assertions.equals(0, None)))

    def test_check_non_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            pgm_args.interpret_py_source_line('exit(1)').as_str,
            tcds_test.Arrangement(),
            tcds_test.Expectation(expected_action_result=result_assertions.equals(1, '')))

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write("on stderr"); exit(2)'
        self._check_single_line_arguments_with_source_variants(
            pgm_args.interpret_py_source_line(python_program).as_str,
            tcds_test.Arrangement(),
            tcds_test.Expectation(expected_action_result=result_assertions.equals(2, 'on stderr')))

    def test_invalid_executable(self):
        self._check_single_line_arguments_with_source_variants(
            '/not/an/executable/program',
            tcds_test.Arrangement(),
            tcds_test.Expectation(acton_raises_hard_error=True))


class TestExecuteInterpret(TestCaseBase):
    def test_check_zero_exit_code__rel_hds_default(self):
        self._check_single_line_arguments_with_source_variants(
            args.sequence([pgm_args.interpret_py_source_file('exit-with-value-on-command-line.py'),
                           0]).as_str,
            tcds_test.Arrangement(
                hds_contents_before=hds_case_dir_contents(DirContents([
                    File('exit-with-value-on-command-line.py',
                         py_pgm_that_exits_with_1st_value_on_command_line(''))]))),
            tcds_test.Expectation(
                expected_action_result=result_assertions.equals(0, None),

            )
        )

    def test_check_zero_exit_code__rel_tmp(self):
        self._check_single_line_arguments_with_source_variants(
            args.sequence([
                pgm_args.interpret_py_source_file(
                    path_arguments.RelOptPathArgument('exit-with-value-on-command-line.py',
                                                      RelOptionType.REL_TMP)),
                0,
            ]).as_str,
            tcds_test.Arrangement(
                sds_contents_before=contents_in(RelSdsOptionType.REL_TMP,
                                                DirContents([
                                                    File('exit-with-value-on-command-line.py',
                                                         py_pgm_that_exits_with_1st_value_on_command_line(''))]))),
            tcds_test.Expectation(
                expected_action_result=result_assertions.equals(0, None)),
        )

    def test_check_non_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            args.sequence([pgm_args.interpret_py_source_file('exit-with-value-on-command-line.py'),
                           2]).as_str,
            tcds_test.Arrangement(
                hds_contents_before=hds_case_dir_contents(DirContents([
                    File('exit-with-value-on-command-line.py',
                         py_pgm_that_exits_with_1st_value_on_command_line('on stderr'))]))),
            tcds_test.Expectation(
                expected_action_result=result_assertions.equals(2, 'on stderr'),

            )
        )

    def test_invalid_executable(self):
        argument = '/not/an/executable/program {} {} {}'.format(args.option(syntax_elements.EXISTING_FILE_OPTION_NAME),
                                                                'exit-with-value-on-command-line.py',
                                                                0)
        self._check_single_line_arguments_with_source_variants(
            argument,
            tcds_test.Arrangement(
                hds_contents_before=hds_case_dir_contents(DirContents([
                    File('exit-with-value-on-command-line.py',
                         py_pgm_that_exits_with_1st_value_on_command_line(''))]))),
            tcds_test.Expectation(
                acton_raises_hard_error=True,

            ))


class TestSource(TestCaseBase):
    def test_check_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            self._python_interpreter_for_source_on_command_line('exit(0)'),
            tcds_test.Arrangement(),
            tcds_test.Expectation(expected_action_result=result_assertions.equals(0, None)))

    def test_check_non_zero_exit_code(self):
        self._check_single_line_arguments_with_source_variants(
            self._python_interpreter_for_source_on_command_line('exit(1)'),
            tcds_test.Arrangement(),
            tcds_test.Expectation(expected_action_result=result_assertions.equals(1, '')))

    def test_check_non_zero_exit_code_with_output_to_stderr(self):
        python_program = 'import sys; sys.stderr.write("on stderr"); exit(2)'
        self._check_single_line_arguments_with_source_variants(
            self._python_interpreter_for_source_on_command_line(python_program),
            tcds_test.Arrangement(),
            tcds_test.Expectation(expected_action_result=result_assertions.equals(2, 'on stderr')))

    @staticmethod
    def _python_interpreter_for_source_on_command_line(argument: str) -> str:
        return pgm_args.interpret_py_source_line(argument).as_str


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
