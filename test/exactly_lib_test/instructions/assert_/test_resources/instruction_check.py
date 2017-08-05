import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.process_execution.os_process_execution import with_no_timeout
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct, ActResultProducer, \
    ActEnvironment, ActResultProducerFromActResult
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction, \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def arrangement(pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                non_home_contents_before_main: non_home_populator.NonHomePopulator = non_home_populator.empty(),
                home_or_sds_contents_before_main: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                act_result_producer: ActResultProducer = ActResultProducerFromActResult(),
                os_services: OsServices = new_default(),
                process_execution_settings=with_no_timeout(),
                symbols: SymbolTable = None,
                ) -> ArrangementPostAct:
    return ArrangementPostAct(pre_contents_population_action=pre_contents_population_action,
                              home_contents=home_dir_contents,
                              sds_contents=sds_contents_before_main,
                              non_home_contents=non_home_contents_before_main,
                              act_result_producer=act_result_producer,
                              os_services=os_services,
                              process_execution_settings=process_execution_settings,
                              home_or_sds_contents=home_or_sds_contents_before_main,
                              symbols=symbols)


class Expectation:
    def __init__(self,
                 validation_post_sds: asrt.ValueAssertion = svh_assertions.is_success(),
                 validation_pre_sds: asrt.ValueAssertion = svh_assertions.is_success(),
                 main_result: asrt.ValueAssertion = pfh_check.is_pass(),
                 symbol_usages: asrt.ValueAssertion = asrt.is_empty_list,
                 main_side_effects_on_files: asrt.ValueAssertion = asrt.anything_goes(),
                 side_effects_check: asrt.ValueAssertion = asrt.anything_goes(),
                 source: asrt.ValueAssertion = asrt.anything_goes(),
                 ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.main_side_effects_on_files = main_side_effects_on_files
        self.side_effects_check = side_effects_check
        self.source = source
        self.symbol_usages = symbol_usages


is_pass = Expectation


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        check(self, parser, source, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: InstructionParser,
          source: ParseSource,
          arrangement: ArrangementPostAct,
          expectation: Expectation):
    Executor(put, arrangement, expectation).execute(parser, source)


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementPostAct,
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
                                  AssertPhaseInstruction,
                                  'The instruction must be an instance of ' + str(AssertPhaseInstruction))
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(instruction, AssertPhaseInstruction)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          instruction.symbol_usages(),
                                                          'symbol-usages after parse')
        with home_and_sds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                home_dir_contents=self.arrangement.home_contents,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_home_contents=self.arrangement.non_home_contents,
                home_or_sds_contents=self.arrangement.home_or_sds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            home_and_sds = path_resolving_environment.home_and_sds
            environment = i.InstructionEnvironmentForPreSdsStep(home_and_sds.hds,
                                                                self.arrangement.process_execution_settings.environ,
                                                                symbols=self.arrangement.symbols)
            validate_result = self._execute_validate_pre_sds(environment, instruction)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_PRE_SDS)
            if not validate_result.is_success:
                return
            environment = i.InstructionEnvironmentForPostSdsStep(
                environment.hds,
                environment.environ,
                home_and_sds.sds,
                phase_identifier.ASSERT.identifier,
                timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                symbols=self.arrangement.symbols)
            validate_result = self._execute_validate_post_setup(environment, instruction)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if not validate_result.is_success:
                return
            self.arrangement.post_sds_population_action.apply(path_resolving_environment)
            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(home_and_sds))
            write_act_result(home_and_sds.sds, act_result)
            self._execute_main(environment, instruction)
            self.expectation.main_side_effects_on_files.apply(self.put, environment.sds)
            self.expectation.side_effects_check.apply(self.put, home_and_sds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)

    def _execute_validate_pre_sds(self,
                                  environment: InstructionEnvironmentForPreSdsStep,
                                  instruction: AssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_sds(environment)
        self.put.assertIsNotNone(result,
                                 'Result from validate method cannot be None')
        self.expectation.validation_pre_sds.apply(self.put, result,
                                                  asrt.MessageBuilder('result of validate/pre sds'))
        return result

    def _execute_validate_post_setup(self,
                                     environment: InstructionEnvironmentForPostSdsStep,
                                     instruction: AssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_post_setup(environment)
        self.put.assertIsNotNone(result,
                                 'Result from validate method cannot be None')
        self.expectation.validation_post_sds.apply(self.put, result,
                                                   asrt.MessageBuilder('result of validate/post setup'))
        return result

    def _execute_main(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      instruction: AssertPhaseInstruction) -> pfh.PassOrFailOrHardError:
        main_result = instruction.main(environment, self.arrangement.os_services)
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.main_result.apply(self.put, main_result)
        self.expectation.main_side_effects_on_files.apply(self.put, environment.sds)
        return main_result
