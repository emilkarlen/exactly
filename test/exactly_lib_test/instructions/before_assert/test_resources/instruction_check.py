import os
import unittest

from exactly_lib.instructions.utils.sub_process_execution import ProcessExecutionSettings
from exactly_lib.instructions.utils.sub_process_execution import with_no_timeout
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.os_services import OsServices, new_default
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct, ActResultProducer, \
    ActEnvironment
from exactly_lib_test.instructions.test_resources.assertion_utils import sh_check, svh_check
from exactly_lib_test.instructions.test_resources.expectations import ExpectationBase
from exactly_lib_test.instructions.test_resources.instruction_check_utils import InstructionExecutionBase
from exactly_lib_test.test_resources import file_structure
from exactly_lib_test.test_resources.execution import sds_populator, utils
from exactly_lib_test.test_resources.execution.utils import write_act_result
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


def arrangement(home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                act_result_producer: ActResultProducer = ActResultProducer(),
                os_services: OsServices = new_default(),
                environ: dict = None,
                process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                ) -> ArrangementPostAct:
    return ArrangementPostAct(home_dir_contents,
                              sds_contents_before_main,
                              act_result_producer,
                              os_services,
                              environ,
                              process_execution_settings)


class Expectation(ExpectationBase):
    def __init__(self,
                 validation_pre_sds: va.ValueAssertion = svh_check.is_success(),
                 validation_post_setup: va.ValueAssertion = svh_check.is_success(),
                 main_result: va.ValueAssertion = sh_check.is_success(),
                 main_side_effects_on_files: va.ValueAssertion = va.anything_goes(),
                 home_and_sds: va.ValueAssertion = va.anything_goes()):
        super().__init__(validation_pre_sds, main_side_effects_on_files, home_and_sds)
        self.validation_post_setup = validation_post_setup
        self.main_result = sh_check.is_sh_and(main_result)


is_success = Expectation


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


class Executor(InstructionExecutionBase):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementPostAct,
                 expectation: Expectation):
        super().__init__(put, arrangement, expectation)
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation
        self.message_builder = va.MessageBuilder()

    def _check(self,
               component: str,
               assertion: va.ValueAssertion,
               actual):
        assertion.apply(self.put,
                        actual,
                        va.MessageBuilder(component))
        return actual

    def execute(self,
                parser: SingleInstructionParser,
                source: SingleInstructionParserSource):
        instruction = parser.apply(source)
        self._check_instruction(BeforeAssertPhaseInstruction, instruction)
        assert isinstance(instruction, BeforeAssertPhaseInstruction)
        with utils.home_and_sds_and_test_as_curr_dir(
                home_dir_contents=self.arrangement.home_contents,
                sds_contents=self.arrangement.sds_contents) as home_and_sds:
            environment = i.InstructionEnvironmentForPreSdsStep(home_and_sds.home_dir_path, self.arrangement.environ)
            validate_result = self._execute_validate_pre_sds(environment, instruction)
            if not validate_result.is_success:
                return
            environment = i.InstructionEnvironmentForPostSdsStep(
                environment.home_directory,
                environment.environ,
                home_and_sds.sds,
                phase_identifier.BEFORE_ASSERT.identifier,
                timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds)
            validate_result = self._execute_validate_post_setup(environment, instruction)
            if not validate_result.is_success:
                return

            act_result = self.arrangement.act_result_producer.apply(ActEnvironment(home_and_sds))
            write_act_result(home_and_sds.sds, act_result)

            self._execute_main(environment, instruction)
            self._check_main_side_effects_on_files(home_and_sds)
            self._check_side_effects_on_home_and_sds(home_and_sds)

    def _execute_validate_pre_sds(
            self,
            global_environment: InstructionEnvironmentForPreSdsStep,
            instruction: BeforeAssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_sds(global_environment)
        self._check_result_of_validate_pre_sds(result)
        return result

    def _execute_validate_post_setup(
            self,
            global_environment: InstructionEnvironmentForPostSdsStep,
            instruction: BeforeAssertPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_post_setup(global_environment)
        self._check('result from validate/post-setup',
                    self.expectation.validation_post_setup,
                    result)
        return result

    def _execute_main(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      instruction: BeforeAssertPhaseInstruction) -> pfh.PassOrFailOrHardError:
        result = instruction.main(environment, self.arrangement.os_services)
        self._check('result from main',
                    self.expectation.main_result,
                    result)
        return result
