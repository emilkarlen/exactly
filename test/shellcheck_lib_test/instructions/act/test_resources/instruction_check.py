import types
import unittest

from shellcheck_lib.script_language.standard_script_language import StandardScriptLanguage
from shellcheck_lib.test_case.os_services import OsServices, new_default
from shellcheck_lib.test_case.sections import common as i
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction
from shellcheck_lib.test_case.sections.act.phase_setup import PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.act.script_source import ScriptSourceBuilder
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib_test.instructions.test_resources import sh_check__va
from shellcheck_lib_test.instructions.test_resources import svh_check__va
from shellcheck_lib_test.instructions.test_resources.arrangements import ArrangementWithEds
from shellcheck_lib_test.instructions.test_resources.expectations import ExpectationBase
from shellcheck_lib_test.instructions.test_resources.instruction_check_utils import InstructionExecutionBase
from shellcheck_lib_test.test_resources import file_structure
from shellcheck_lib_test.test_resources import value_assertion as va
from shellcheck_lib_test.test_resources.execution import eds_populator, utils


class Arrangement(ArrangementWithEds):
    def __init__(self,
                 source_builder: ScriptSourceBuilder =
                 ScriptSourceBuilder(StandardScriptLanguage()),
                 home_dir_contents: file_structure.DirContents = file_structure.DirContents([]),
                 eds_contents_before_main: eds_populator.EdsPopulator = eds_populator.empty(),
                 os_services: OsServices = new_default()):
        super().__init__(home_dir_contents, eds_contents_before_main, os_services)
        self.source_builder = source_builder


class Expectation(ExpectationBase):
    def __init__(self, validation_pre_eds: va.ValueAssertion = svh_check__va.is_success(),
                 validation_post_setup: va.ValueAssertion = svh_check__va.is_success(),
                 main_result: va.ValueAssertion = sh_check__va.is_success(),
                 main_side_effects_on_script_source: va.ValueAssertion = va.anything_goes(),
                 main_side_effects_on_files: va.ValueAssertion = va.anything_goes(),
                 home_and_eds: va.ValueAssertion = va.anything_goes()):
        super().__init__(validation_pre_eds, main_side_effects_on_files, home_and_eds)
        self.validation_post_setup = validation_post_setup
        self.main_result = sh_check__va.is_sh_and(main_result)
        self.main_side_effects_on_script_source = main_side_effects_on_script_source


is_success = Expectation


class TestCaseBase(unittest.TestCase):
    def _check(self,
               instruction_constructor: types.FunctionType,
               source: str,
               arrangement: Arrangement,
               expectation: Expectation):
        check(self, instruction_constructor, source, arrangement, expectation)


def check(put: unittest.TestCase,
          instruction_constructor: types.FunctionType,
          source: str,
          arrangement: Arrangement,
          expectation: Expectation):
    Executor(put, arrangement, expectation).execute(instruction_constructor, source)


class Executor(InstructionExecutionBase):
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: Arrangement,
                 expectation: Expectation):
        super().__init__(put, arrangement, expectation)
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
                instruction_constructor: types.FunctionType,
                source: str):
        instruction = instruction_constructor(source)
        self._check_instruction(ActPhaseInstruction, instruction)
        assert isinstance(instruction, ActPhaseInstruction)
        with utils.home_and_eds_and_test_as_curr_dir(
                home_dir_contents=self.arrangement.home_contents,
                eds_contents=self.arrangement.eds_contents) as home_and_eds:
            environment = i.GlobalEnvironmentForPreEdsStep(home_and_eds.home_dir_path)
            validate_result = self._execute_validate_pre_eds(environment, instruction)
            if not validate_result.is_success:
                return
            environment = i.GlobalEnvironmentForPostEdsPhase(home_and_eds.home_dir_path,
                                                             home_and_eds.eds)
            validate_result = self._execute_validate_post_setup(environment, instruction)
            if not validate_result.is_success:
                return
            self._execute_main(environment, instruction)
            self._check_main_side_effects_on_script_source()
            self._check_main_side_effects_on_files(home_and_eds)
            self._check_side_effects_on_home_and_eds(home_and_eds)

    def _execute_validate_pre_eds(
            self,
            global_environment: GlobalEnvironmentForPreEdsStep,
            instruction: ActPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_pre_eds(global_environment)
        self._check_result_of_validate_pre_eds(result)
        return result

    def _execute_validate_post_setup(
            self,
            global_environment: GlobalEnvironmentForPostEdsPhase,
            instruction: ActPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        result = instruction.validate_post_setup(global_environment)
        self._check('result from validate/post-setup',
                    self.expectation.validation_post_setup,
                    result)
        return result

    def _execute_main(self,
                      environment: GlobalEnvironmentForPostEdsPhase,
                      instruction: ActPhaseInstruction) -> pfh.PassOrFailOrHardError:
        result = instruction.main(environment,
                                  PhaseEnvironmentForScriptGeneration(self.arrangement.source_builder))
        self._check('result from main',
                    self.expectation.main_result,
                    result)
        return result

    def _check_main_side_effects_on_script_source(self):
        self.expectation.main_side_effects_on_script_source.apply(self.put,
                                                                  self.arrangement.source_builder)
