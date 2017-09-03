import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.util.process_execution.os_process_execution import ProcessExecutionSettings, with_no_timeout
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct, ActResultProducer, \
    ActEnvironment, ActResultProducerFromActResult
from exactly_lib_test.instructions.test_resources.expectations import ExpectationBase
from exactly_lib_test.instructions.test_resources.instruction_check_utils import InstructionExecutionBase
from exactly_lib_test.test_case.test_resources import sh_assertions
from exactly_lib_test.test_case_file_structure.test_resources import non_home_populator, home_populators
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_utils import write_act_result
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction, home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def arrangement(pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                hds_contents: home_populators.HomePopulator = home_populators.empty(),
                sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                non_home_contents_before_main: non_home_populator.NonHomePopulator = non_home_populator.empty(),
                home_or_sds_contents: home_and_sds_populators.HomeOrSdsPopulator = home_and_sds_populators.empty(),
                act_result_producer: ActResultProducer = ActResultProducerFromActResult(),
                os_services: OsServices = new_default(),
                process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                symbols: SymbolTable = None,
                ) -> ArrangementPostAct:
    return ArrangementPostAct(pre_contents_population_action=pre_contents_population_action,
                              hds_contents=hds_contents,
                              sds_contents=sds_contents_before_main,
                              non_home_contents=non_home_contents_before_main,
                              home_or_sds_contents=home_or_sds_contents,
                              act_result_producer=act_result_producer,
                              os_services=os_services,
                              process_execution_settings=process_execution_settings,
                              symbols=symbols)


class Expectation(ExpectationBase):
    def __init__(self,
                 validation_pre_sds: asrt.ValueAssertion = svh_assertions.is_success(),
                 validation_post_setup: asrt.ValueAssertion = svh_assertions.is_success(),
                 main_result: asrt.ValueAssertion = sh_assertions.is_success(),
                 symbol_usages: asrt.ValueAssertion = asrt.is_empty_list,
                 main_side_effects_on_files: asrt.ValueAssertion = asrt.anything_goes(),
                 home_and_sds: asrt.ValueAssertion = asrt.anything_goes(),
                 source: asrt.ValueAssertion = asrt.anything_goes(),
                 ):
        super().__init__(validation_pre_sds, main_side_effects_on_files, home_and_sds)
        self.validation_post_setup = validation_post_setup
        self.main_result = sh_assertions.is_sh_and(main_result)
        self.source = source
        self.symbol_usages = symbol_usages


is_success = Expectation


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


class Executor(InstructionExecutionBase):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementPostAct,
                 expectation: Expectation):
        super().__init__(put, arrangement, expectation)
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation
        self.message_builder = asrt.MessageBuilder()

    def _check(self,
               component: str,
               assertion: asrt.ValueAssertion,
               actual):
        assertion.apply(self.put,
                        actual,
                        asrt.MessageBuilder(component))
        return actual

    def execute(self,
                parser: InstructionParser,
                source: ParseSource):
        instruction = parser.parse(source)
        self._check_instruction(BeforeAssertPhaseInstruction, instruction)
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(instruction, BeforeAssertPhaseInstruction)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          instruction.symbol_usages(),
                                                          'symbol-usages after parse')
        with home_and_sds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_home_contents=self.arrangement.non_home_contents,
                home_or_sds_contents=self.arrangement.home_or_sds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            home_and_sds = path_resolving_environment.home_and_sds
            self.arrangement.post_sds_population_action.apply(path_resolving_environment)
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
                phase_identifier.BEFORE_ASSERT.identifier,
                timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                symbols=self.arrangement.symbols)
            validate_result = self._execute_validate_post_setup(environment, instruction)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if not validate_result.is_success:
                return

            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(home_and_sds))
            write_act_result(home_and_sds.sds, act_result)

            self._execute_main(environment, instruction)
            self._check_main_side_effects_on_files(home_and_sds)
            self._check_side_effects_on_home_and_sds(home_and_sds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)

    def _execute_validate_pre_sds(
            self,
            environment: InstructionEnvironmentForPreSdsStep,
            instruction: BeforeAssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_sds(environment)
        self._check_result_of_validate_pre_sds(result)
        return result

    def _execute_validate_post_setup(
            self,
            environment: InstructionEnvironmentForPostSdsStep,
            instruction: BeforeAssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_post_setup(environment)
        self._check('result from validate/post-setup',
                    self.expectation.validation_post_setup,
                    result)
        return result

    def _execute_main(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      instruction: BeforeAssertPhaseInstruction) -> sh.SuccessOrHardError:
        result = instruction.main(environment, self.arrangement.os_services)
        self._check('result from main',
                    self.expectation.main_result,
                    result)
        return result
