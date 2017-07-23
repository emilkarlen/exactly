import pathlib
import sys
import unittest

from exactly_lib.act_phase_setups import file_interpreter as sut
from exactly_lib.test_case.act_phase_handling import ParseException
from exactly_lib.util.process_execution.os_process_execution import Command
from exactly_lib.util.string import lines_content
from exactly_lib_test.act_phase_setups.file_interpreter.configuration import TheConfigurationBase
from exactly_lib_test.act_phase_setups.test_resources import act_phase_execution
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_file_rel_home as single_file_rel_home
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import suite_for_execution
from exactly_lib_test.act_phase_setups.test_resources.test_validation_for_single_line_source import \
    TestCaseForConfigurationForValidation
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.act_phase_os_process_executor import \
    ActPhaseOsProcessExecutorThatRecordsArguments
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file


class TheConfiguration(TheConfigurationBase):
    def __init__(self):
        super().__init__(sut.constructor(Command([sys.executable], shell=False)))


def suite() -> unittest.TestSuite:
    tests = []
    the_configuration = TheConfiguration()
    tests.append(suite_for(the_configuration))
    tests.append(suite_for_execution(the_configuration))
    return unittest.TestSuite(tests)


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
        with self.assertRaises(ParseException):
            self._do_parse(act_phase_instructions,
                           home_dir_contents=DirContents([empty_file('valid-file-ref')]))


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
    def __init__(self, configuration: Configuration):
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


def _instructions_for_file_in_home_dir(home_dir_path: pathlib.Path, statements: list) -> list:
    with open(str(home_dir_path / 'sut.py'), 'w') as f:
        f.write(lines_content(statements))
    return [instr(['sut.py'])]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
