import copy
import pathlib
import tempfile
import unittest
from time import strftime, localtime

from exactly_lib import program_info
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh
from exactly_lib_test.execution.test_resources.act_source_executor import act_phase_handling_that_runs_constant_actions
from exactly_lib_test.instructions.configuration.test_resources import configuration_check as config_check
from exactly_lib_test.instructions.test_resources import sh_check
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementBase
from exactly_lib_test.test_resources import file_structure


class Arrangement(ArrangementBase):
    def __init__(self,
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 initial_configuration_builder: ConfigurationBuilder = ConfigurationBuilder(pathlib.Path('.'),
                                                                                            act_phase_handling_that_runs_constant_actions())):
        super().__init__(home_dir_contents)
        self.initial_configuration_builder = initial_configuration_builder


class Expectation:
    def __init__(self,
                 main_result: sh_check.Assertion = sh_check.IsSuccess(),
                 configuration: config_check.Assertion = config_check.AnythingGoes(),
                 ):
        self.main_result = main_result
        self.configuration = configuration


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: SingleInstructionParser,
               source: SingleInstructionParserSource,
               arrangement: Arrangement,
               expectation: Expectation):
        Executor(self, arrangement, expectation).execute(parser, source)


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
                 expectation: Expectation):
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation

    def execute(self,
                parser: SingleInstructionParser,
                source: SingleInstructionParserSource):
        instruction = parser.apply(source)
        self.put.assertIsNotNone(instruction,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(instruction,
                                  ConfigurationPhaseInstruction,
                                  'The instruction must be an instance of ' + str(ConfigurationPhaseInstruction))
        assert isinstance(instruction, ConfigurationPhaseInstruction)
        prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
        with tempfile.TemporaryDirectory(prefix=prefix + "-home-") as home_dir_name:
            home_dir_path = pathlib.Path(home_dir_name).resolve()
            self.arrangement.home_contents.write_to(home_dir_path)
            configuration_builder = self.arrangement.initial_configuration_builder
            configuration_builder.set_home_dir(home_dir_path)
            self._execute_main(configuration_builder,
                               instruction)

    def _execute_main(self,
                      configuration_builder: ConfigurationBuilder,
                      instruction: ConfigurationPhaseInstruction) -> sh.SuccessOrHardError:
        initial_configuration_builder = copy.deepcopy(configuration_builder)
        main_result = instruction.main(None, configuration_builder)
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.main_result.apply(self.put, main_result)
        self.expectation.configuration.apply(self.put,
                                             initial_configuration_builder,
                                             configuration_builder)
        return main_result
