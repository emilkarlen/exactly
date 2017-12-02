import copy
import unittest
from time import strftime, localtime

from exactly_lib import program_info
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case.act_phase_handling import ActPhaseHandling
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, ConfigurationBuilder
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.test_case_status import ExecutionMode
from exactly_lib_test.execution.partial_execution.test_resources.basic import dummy_act_phase_handling
from exactly_lib_test.instructions.configuration.test_resources import configuration_check as config_check
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementBase
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_file_structure.test_resources.hds_utils import home_directory_structure
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Arrangement(ArrangementBase):
    def __init__(self,
                 hds_contents: home_populators.HomePopulator = home_populators.empty(),
                 act_phase_handling: ActPhaseHandling = dummy_act_phase_handling(),
                 execution_mode: ExecutionMode = ExecutionMode.NORMAL,
                 timeout_in_seconds: int = None):
        super().__init__(hds_contents=hds_contents)
        self.act_phase_handling = act_phase_handling
        self.execution_mode = execution_mode
        self.timeout_in_seconds = timeout_in_seconds


class Expectation:
    def __init__(self,
                 main_result: asrt.ValueAssertion = sh_assertions.is_success(),
                 configuration: config_check.Assertion = config_check.AnythingGoes(),
                 source: asrt.ValueAssertion = asrt.anything_goes(),
                 ):
        self.main_result = main_result
        self.configuration = configuration
        self.source = source


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
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
                parser: InstructionParser,
                source: ParseSource):
        instruction = parser.parse(source)
        self.put.assertIsNotNone(instruction,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(instruction,
                                  ConfigurationPhaseInstruction,
                                  'The instruction must be an instance of ' + str(ConfigurationPhaseInstruction))
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(instruction, ConfigurationPhaseInstruction)
        prefix = strftime(program_info.PROGRAM_NAME + '-test-%Y-%m-%d-%H-%M-%S', localtime())
        with home_directory_structure(prefix=prefix + '-home',
                                      contents=self.arrangement.hds_contents,
                                      ) as hds:
            configuration_builder = ConfigurationBuilder(hds.case_dir,
                                                         hds.act_dir,
                                                         self.arrangement.act_phase_handling,
                                                         timeout_in_seconds=self.arrangement.timeout_in_seconds)
            configuration_builder.set_execution_mode(self.arrangement.execution_mode)
            self._execute_main(configuration_builder,
                               instruction)

    def _execute_main(self,
                      configuration_builder: ConfigurationBuilder,
                      instruction: ConfigurationPhaseInstruction) -> sh.SuccessOrHardError:
        initial_configuration_builder = copy.deepcopy(configuration_builder)
        main_result = instruction.main(configuration_builder)
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.main_result.apply_with_message(self.put, main_result,
                                                        'result of main')
        self.expectation.configuration.apply(self.put,
                                             initial_configuration_builder,
                                             configuration_builder)
        return main_result
