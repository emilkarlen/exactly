import unittest

from exactly_lib.act_phase_setups import file_interpreter as sut
from exactly_lib.util.process_execution.os_process_execution import Command
from exactly_lib_test.act_phase_setups.file_interpreter import test_resources
from exactly_lib_test.act_phase_setups.file_interpreter.configuration import TheConfigurationBase
from exactly_lib_test.act_phase_setups.test_resources import act_phase_execution
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_file_rel_home as single_file_rel_home
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import suite_for_execution
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.act_phase_os_process_executor import \
    ActPhaseOsProcessExecutorThatRecordsArguments
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.programs.python_program_execution import abs_path_to_interpreter_quoted_for_exactly

COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE = Command(abs_path_to_interpreter_quoted_for_exactly(), shell=True)


class TheConfiguration(TheConfigurationBase):
    def __init__(self):
        super().__init__(sut.constructor(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE))


def suite_for(configuration: TheConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        single_file_rel_home.suite_for(configuration),
        custom_suite_for(configuration),

        test_resources.suite_for(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE),
    ])


def custom_suite_for(conf: TheConfiguration) -> unittest.TestSuite:
    test_cases = [
        # TestDoNotFailWhenThereAreArgumentsButTheyAreInvalidlyQuoted,
        TestFileReferenceCanBeQuoted,
        TestArgumentsAreParsedAndPassedToExecutor,
    ]
    return unittest.TestSuite([tc(conf) for tc in test_cases])


def suite() -> unittest.TestSuite:
    tests = []
    the_configuration = TheConfiguration()
    tests.append(suite_for(the_configuration))
    tests.append(suite_for_execution(the_configuration))
    return unittest.TestSuite(tests)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


# TODO Not sure if this case should be supported.
# class TestDoNotFailWhenThereAreArgumentsButTheyAreInvalidlyQuoted(TestCaseForConfigurationForValidation):
#     def runTest(self):
#         act_phase_instructions = [instr(["""valid-file-ref 'quoting missing ending single-quote"""]),
#                                   instr([''])]
#         actual = self._do_parse_and_validate_pre_sds(act_phase_instructions,
#                                                      home_dir_contents=DirContents([empty_file('valid-file-ref')]))
#         self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
#                       actual.status,
#                       'Validation result')


class TestFileReferenceCanBeQuoted(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.configuration))

    def runTest(self):
        act_phase_instructions = [instr(["""'quoted file name.src'"""]),
                                  instr([''])]
        executor_that_records_arguments = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = act_phase_execution.Arrangement(home_dir_contents=DirContents(
                                                          [empty_file('quoted file name.src')]),
                                                      act_phase_process_executor=executor_that_records_arguments)
        expectation = act_phase_execution.Expectation()
        act_phase_execution.check_execution(self,
                                            self.configuration.sut,
                                            act_phase_instructions,
                                            arrangement, expectation)
        actual_command = executor_that_records_arguments.command
        self.assertTrue(actual_command.shell,
                        'Should be executed as a shell command')
        self.assertIsInstance(actual_command.args,
                              str,
                              'Argument is expected to be a str for shell commands')


class TestArgumentsAreParsedAndPassedToExecutor(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.configuration))

    def runTest(self):
        act_phase_instructions = [instr(["""existing-file.src un-quoted 'single quoted' "double-quoted" """])]
        should_be_last_part_of_command_line = """un-quoted 'single quoted' "double-quoted\""""
        executor_that_records_arguments = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = act_phase_execution.Arrangement(home_dir_contents=DirContents([empty_file('existing-file.src')]),
                                                      act_phase_process_executor=executor_that_records_arguments)
        expectation = act_phase_execution.Expectation()
        act_phase_execution.check_execution(self,
                                            self.configuration.sut,
                                            act_phase_instructions,
                                            arrangement,
                                            expectation)
        self.assertTrue(executor_that_records_arguments.command.shell,
                        'Should be executed as a shell command')
        self.assertIsInstance(executor_that_records_arguments.command.args,
                              str,
                              'Argument should be a single string when for shell command')
        self.assertEqual(should_be_last_part_of_command_line,
                         executor_that_records_arguments.command.args[-(len(should_be_last_part_of_command_line)):])
