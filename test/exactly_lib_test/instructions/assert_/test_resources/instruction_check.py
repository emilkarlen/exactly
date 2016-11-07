import unittest

from exactly_lib.instructions.utils.sub_process_execution import with_no_timeout
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct, ActResultProducer, \
    ActEnvironment
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check, svh_check
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.execution import sds_populator, utils
from exactly_lib_test.test_resources.execution.utils import write_act_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def arrangement(home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                eds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                act_result_producer: ActResultProducer = ActResultProducer(),
                os_services: OsServices = new_default(),
                process_execution_settings=with_no_timeout(),
                ) -> ArrangementPostAct:
    return ArrangementPostAct(home_dir_contents,
                              eds_contents_before_main,
                              act_result_producer,
                              os_services,
                              process_execution_settings)


class Expectation:
    def __init__(self,
                 validation_post_sds: va.ValueAssertion = svh_check.is_success(),
                 validation_pre_sds: va.ValueAssertion = svh_check.is_success(),
                 main_result: va.ValueAssertion = pfh_check.is_pass(),
                 main_side_effects_on_files: va.ValueAssertion = va.anything_goes(),
                 side_effects_check: va.ValueAssertion = va.anything_goes(),
                 ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.main_side_effects_on_files = main_side_effects_on_files
        self.side_effects_check = side_effects_check


is_pass = Expectation


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: SingleInstructionParser,
               source: SingleInstructionParserSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        check(self, parser, source, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: SingleInstructionParser,
          source: SingleInstructionParserSource,
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
                parser: SingleInstructionParser,
                source: SingleInstructionParserSource):
        instruction = parser.apply(source)
        self.put.assertIsNotNone(instruction,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(instruction,
                                  AssertPhaseInstruction,
                                  'The instruction must be an instance of ' + str(AssertPhaseInstruction))
        assert isinstance(instruction, AssertPhaseInstruction)
        with utils.home_and_sds_and_test_as_curr_dir(
                home_dir_contents=self.arrangement.home_contents,
                sds_contents=self.arrangement.eds_contents) as home_and_sds:
            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(home_and_sds))
            write_act_result(home_and_sds.sds, act_result)
            # TODO Execution of validate/pre-sds should be done before act-result is written.
            # But cannot do this for the moment, since many tests write home-dir contents
            # as part of the act-result.
            environment = i.InstructionEnvironmentForPreSdsStep(home_and_sds.home_dir_path)
            validate_result = self._execute_validate_pre_sds(environment, instruction)
            if not validate_result.is_success:
                return
            environment = i.InstructionEnvironmentForPostSdsStep(
                home_and_sds.home_dir_path,
                home_and_sds.sds,
                phase_identifier.ASSERT.identifier,
                timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds)
            validate_result = self._execute_validate_post_setup(environment, instruction)
            if not validate_result.is_success:
                return
            self._execute_main(environment, instruction)
            self.expectation.main_side_effects_on_files.apply(self.put, environment.sds)
            self.expectation.side_effects_check.apply(self.put, home_and_sds)

    def _execute_validate_pre_sds(self,
                                  global_environment: InstructionEnvironmentForPreSdsStep,
                                  instruction: AssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_sds(global_environment)
        self.put.assertIsNotNone(result,
                                 'Result from validate method cannot be None')
        self.expectation.validation_pre_sds.apply(self.put, result,
                                                  va.MessageBuilder('result of validate/pre sds'))
        return result

    def _execute_validate_post_setup(self,
                                     global_environment: InstructionEnvironmentForPostSdsStep,
                                     instruction: AssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_post_setup(global_environment)
        self.put.assertIsNotNone(result,
                                 'Result from validate method cannot be None')
        self.expectation.validation_post_sds.apply(self.put, result,
                                                   va.MessageBuilder('result of validate/post setup'))
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
