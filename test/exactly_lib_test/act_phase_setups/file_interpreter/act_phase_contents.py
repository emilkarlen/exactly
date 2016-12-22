import unittest

from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.act_phase_setups.file_interpreter.configuration import TheConfiguration
from exactly_lib_test.act_phase_setups.test_resources import act_phase_execution
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_file_rel_home as single_file_rel_home
from exactly_lib_test.act_phase_setups.test_resources.test_validation_for_single_line_source import \
    TestCaseForConfigurationForValidation
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.act_phase_os_process_executor import \
    ActPhaseOsProcessExecutorThatRecordsArguments
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file


def suite_for(configuration: TheConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        single_file_rel_home.suite_for(configuration),
        custom_suite_for(configuration)
    ])


def custom_suite_for(conf: TheConfiguration) -> unittest.TestSuite:
    test_cases = [
        TestFailWhenThereAreArgumentsButTheyAreInvalidlyQuoted,
        TestFileReferenceCanBeQuoted,
        TestArgumentsAreParsedAndPassedToExecutor,
    ]
    return unittest.TestSuite([tc(conf) for tc in test_cases])


class TestFailWhenThereAreArgumentsButTheyAreInvalidlyQuoted(TestCaseForConfigurationForValidation):
    def runTest(self):
        act_phase_instructions = [instr(["""valid-file-ref 'quoting missing ending single-quote"""]),
                                  instr([''])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')


class TestFileReferenceCanBeQuoted(unittest.TestCase):
    def __init__(self, configuration: TheConfiguration):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.configuration))

    def runTest(self):
        act_phase_instructions = [instr(["""'quoted file name.src'"""]),
                                  instr([''])]
        executor_that_records_arguments = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = act_phase_execution.Arrangement(self.configuration.sut,
                                                      act_phase_instructions,
                                                      home_dir_contents=DirContents(
                                                          [empty_file('quoted file name.src')]),
                                                      act_phase_process_executor=executor_that_records_arguments)
        expectation = act_phase_execution.Expectation()
        act_phase_execution.check_execution(self, arrangement, expectation)
        self.assertFalse(executor_that_records_arguments.command.shell,
                         'Should not be executed as a shell command')
        self.assertEqual(2,
                         len(executor_that_records_arguments.command.args),
                         'Number of command-and-arguments, including interpreter')


class TestArgumentsAreParsedAndPassedToExecutor(unittest.TestCase):
    def __init__(self, configuration: TheConfiguration):
        super().__init__()
        self.configuration = configuration

    def shortDescription(self):
        return str(type(self)) + '/' + str(type(self.configuration))

    def runTest(self):
        act_phase_instructions = [instr(["""existing-file.src un-quoted 'single quoted' "double-quoted" """]),
                                  instr([''])]
        executor_that_records_arguments = ActPhaseOsProcessExecutorThatRecordsArguments()
        arrangement = act_phase_execution.Arrangement(self.configuration.sut,
                                                      act_phase_instructions,
                                                      home_dir_contents=DirContents([empty_file('existing-file.src')]),
                                                      act_phase_process_executor=executor_that_records_arguments)
        expectation = act_phase_execution.Expectation()
        act_phase_execution.check_execution(self, arrangement, expectation)
        self.assertFalse(executor_that_records_arguments.command.shell,
                         'Should not be executed as a shell command')
        self.assertEqual(5,
                         len(executor_that_records_arguments.command.args),
                         'Number of command-and-arguments, including interpreter')
        self.assertListEqual(['un-quoted', 'single quoted', 'double-quoted'],
                             executor_that_records_arguments.command.args[2:])
