import os
import unittest

from exactly_lib.instructions.multi_phase import run as sut
from exactly_lib.instructions.multi_phase.utils.instruction_from_parts_for_executing_program import \
    TheInstructionEmbryo, ExecutionResultAndStderr
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case import os_services
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelOptionType
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.util.process_execution.execution_elements import with_environ
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.multi_phase.test_resources import instruction_embryo_check
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import single_line_source
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_case_file_structure.test_resources.hds_populators import hds_case_dir_contents
from exactly_lib_test.test_case_file_structure.test_resources.sds_populator import contents_in
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args, result_assertions
from exactly_lib_test.test_case_utils.test_resources import arguments_building as args
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
                                                                            'single line description')),
    ])


class ExecuteAction(TcdsAction):
    def __init__(self, instruction_embryo: TheInstructionEmbryo):
        self.instruction_embryo = instruction_embryo

    def apply(self, environment: PathResolvingEnvironmentPreOrPostSds) -> ExecutionResultAndStderr:
        environment_builder = InstructionEnvironmentPostSdsBuilder.new_tcds(
            environment.tcds,
            process_execution_settings=with_environ(dict(os.environ)),
        )
        return self.instruction_embryo.main(
            environment_builder.build_post_sds(),
            os_services.new_default(),
        )


class EmbryoTestCaseBase(unittest.TestCase):
    def _check_single_line_arguments_with_source_variants(
            self,
            instruction_argument: str,
            arrangement: ArrangementWithSds,
            expectation: instruction_embryo_check.Expectation[ExecutionResultAndStderr],
    ):
        for source in equivalent_source_variants__with_source_check__consume_last_line(self, instruction_argument):
            self._check(source, arrangement, expectation)

    def _check(self,
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: instruction_embryo_check.Expectation[ExecutionResultAndStderr],
               ):
        parser = sut.embryo_parser('instruction-name')
        instruction_embryo_check.check(self, parser, source, arrangement, expectation)


class TestCaseBase(tcds_test.TestCaseBase):
    def _check_single_line_arguments_with_source_variants(self,
                                                          instruction_argument: str,
                                                          arrangement: tcds_test.Arrangement,
                                                          expectation: tcds_test.Expectation):
        for source in equivalent_source_variants__with_source_check__consume_last_line(self, instruction_argument):
            embryo_parser = sut.embryo_parser('instruction-name')
            instruction_embryo = embryo_parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
            action = ExecuteAction(instruction_embryo)
            self._check(action, arrangement, expectation)

    def _check_source(self,
                      source: ParseSource,
                      arrangement: tcds_test.Arrangement,
                      expectation: tcds_test.Expectation):
        instruction_embryo = sut.embryo_parser('instruction-name').parse(source)
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
            args.sequence([pgm_args.interpret_py_source_file(
                args.path_rel_opt('exit-with-value-on-command-line.py',
                                  RelOptionType.REL_TMP)),
                0]).as_str,
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
    def test_parse_should_fail_when_no_source_argument(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            sut.program_parser().parse(
                single_line_source('EXECUTABLE %s' % syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER))

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
