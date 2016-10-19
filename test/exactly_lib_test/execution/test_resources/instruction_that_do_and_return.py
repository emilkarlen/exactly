import pathlib
import types
from pathlib import Path

from exactly_lib.execution import phases, phase_step
from exactly_lib.execution.phase_step import PhaseStep
from exactly_lib.section_document import model
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.act.instruction import PhaseEnvironmentForScriptGeneration, ActPhaseInstruction
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction
from exactly_lib.test_case.phases.configuration import ConfigurationBuilder, \
    ConfigurationPhaseInstruction
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib_test.execution.full_execution.test_resources.test_case_generator import \
    TestCaseGeneratorForFullExecutionBase
from exactly_lib_test.execution.test_resources import python_code_gen as py
from exactly_lib_test.execution.test_resources.instruction_test_resources import cleanup_phase_instruction_that, \
    before_assert_phase_instruction_that, setup_phase_instruction_that, configuration_phase_instruction_that, \
    assert_phase_instruction_that, act_phase_instruction_with_source
from exactly_lib_test.execution.test_resources.test_case_generation import instruction_line_constructor, \
    phase_contents


def do_nothing__configuration_phase(phase_step: PhaseStep,
                                    phase_environment: ConfigurationBuilder):
    pass


def do_nothing__pre_eds(phase_step: PhaseStep,
                        home_dir: Path):
    pass


def do_nothing__post_eds(phase_step: PhaseStep,
                         global_environment: i.GlobalEnvironmentForPostEdsPhase):
    pass


def do_nothing__generate_script(global_environment: i.GlobalEnvironmentForPostEdsPhase,
                                phase_environment: PhaseEnvironmentForScriptGeneration):
    pass


class TestCaseSetup(tuple):
    def __new__(cls,
                ret_val_from_validate: svh.SuccessOrValidationErrorOrHardError = svh.new_svh_success(),
                ret_val_from_main: sh.SuccessOrHardError = sh.new_sh_success(),
                ret_val_from_assert_main: pfh.PassOrFailOrHardError = pfh.new_pfh_pass(),
                validation_action__pre_eds: types.FunctionType = do_nothing__pre_eds,
                configuration_phase_action: types.FunctionType = do_nothing__configuration_phase,
                validation_action__post_eds: types.FunctionType = do_nothing__post_eds,
                main_action__post_eds: types.FunctionType = do_nothing__post_eds,
                main__generate_script: types.FunctionType = do_nothing__generate_script,
                ):
        return tuple.__new__(cls, (ret_val_from_validate,
                                   ret_val_from_main,
                                   ret_val_from_assert_main,
                                   validation_action__pre_eds,
                                   configuration_phase_action,
                                   validation_action__post_eds,
                                   main_action__post_eds,
                                   main__generate_script,
                                   ))

    def as_configuration_phase_instruction(self) -> ConfigurationPhaseInstruction:
        return configuration_phase_instruction_that(main=self._do_configuration_main())

    def as_setup_phase_instruction(self) -> SetupPhaseInstruction:
        return setup_phase_instruction_that(
            validate_pre_eds=self._do_validate_pre_eds(phase_step.SETUP__VALIDATE_PRE_EDS),
            validate_post_setup=self._do_validate_post_eds(phase_step.SETUP__VALIDATE_POST_SETUP),
            main=self._do_main(phase_step.SETUP__MAIN))

    def as_act_phase_instruction(self) -> ActPhaseInstruction:
        return act_phase_instruction_with_source()

    def as_before_assert_phase_instruction(self) -> BeforeAssertPhaseInstruction:
        return before_assert_phase_instruction_that(
            validate_pre_eds=self._do_validate_pre_eds(phase_step.BEFORE_ASSERT__VALIDATE_PRE_EDS),
            validate_post_setup=self._do_validate_post_eds(phase_step.BEFORE_ASSERT__VALIDATE_POST_SETUP),
            main=self._do_main(phase_step.BEFORE_ASSERT__MAIN))

    def as_assert_phase_instruction(self) -> AssertPhaseInstruction:
        return assert_phase_instruction_that(
            validate_pre_eds=self._do_validate_pre_eds(phase_step.ASSERT__VALIDATE_PRE_EDS),
            validate_post_setup=self._do_validate_post_eds(phase_step.ASSERT__VALIDATE_POST_SETUP),
            main=self._do_assert_main())

    def as_cleanup_phase_instruction(self) -> CleanupPhaseInstruction:
        return cleanup_phase_instruction_that(
            validate_pre_eds=self._do_validate_pre_eds(phase_step.CLEANUP__VALIDATE_PRE_EDS),
            main=self._do_main(phase_step.CLEANUP__MAIN))

    @property
    def ret_val_from_validate(self) -> svh.SuccessOrValidationErrorOrHardError:
        return self[0]

    @property
    def ret_val_from_main(self) -> sh.SuccessOrHardError:
        return self[1]

    @property
    def ret_val_from_assert_main(self) -> pfh.PassOrFailOrHardError:
        return self[2]

    @property
    def validation_action__without_eds(self) -> types.FunctionType:
        return self[3]

    @property
    def configuration_phase_action(self) -> types.FunctionType:
        return self[4]

    @property
    def validation_action__with_eds(self) -> types.FunctionType:
        return self[5]

    @property
    def execution_action__with_eds(self) -> types.FunctionType:
        return self[6]

    def _do_validate_pre_eds(self,
                             the_phase_step: PhaseStep):
        def ret_val(environment: i.GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
            self.validation_action__without_eds(the_phase_step,
                                                environment.home_directory)
            return self.ret_val_from_validate

        return ret_val

    def _do_validate_post_eds(self,
                              the_phase_step: PhaseStep):
        def ret_val(environment: i.GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
            self.validation_action__with_eds(the_phase_step,
                                             environment)
            return self.ret_val_from_validate

        return ret_val

    def _do_main(self,
                 the_phase_step: PhaseStep):
        def ret_val(environment: i.GlobalEnvironmentForPostEdsPhase, *args):
            self.execution_action__with_eds(the_phase_step,
                                            environment)
            return self.ret_val_from_main

        return ret_val

    def _do_configuration_main(self):
        def ret_val(global_environment, configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
            self.configuration_phase_action(phase_step.CONFIGURATION__MAIN,
                                            configuration_builder)
            return self.ret_val_from_main

        return ret_val

    def _do_assert_main(self):
        def ret_val(environment: i.GlobalEnvironmentForPostEdsPhase, *args) -> pfh.PassOrFailOrHardError:
            self.execution_action__with_eds(phase_step.ASSERT__MAIN,
                                            environment)
            return self.ret_val_from_assert_main

        return ret_val


class TestCaseGeneratorForTestCaseSetup(TestCaseGeneratorForFullExecutionBase):
    """
    Generation of a Test Case from a TestCaseSetup.

    The generated Test Case will have a single instruction for each phase.
    """

    def __init__(self,
                 setup: TestCaseSetup):
        super().__init__()
        self.setup = setup
        self.instruction_line_constructor = instruction_line_constructor()

    def phase_contents_for(self, phase: phases.Phase) -> model.SectionContents:
        instr = None
        if phase == phases.CONFIGURATION:
            instr = self.setup.as_configuration_phase_instruction()
        if phase == phases.SETUP:
            instr = self.setup.as_setup_phase_instruction()
        if phase == phases.ACT:
            instr = self.setup.as_act_phase_instruction()
        if phase == phases.BEFORE_ASSERT:
            instr = self.setup.as_before_assert_phase_instruction()
        if phase == phases.ASSERT:
            instr = self.setup.as_assert_phase_instruction()
        if phase == phases.CLEANUP:
            instr = self.setup.as_cleanup_phase_instruction()
        if instr is None:
            raise ValueError('Unknown phase: ' + str(phase))
        return phase_contents([self.instruction_line_constructor.apply(instr)])


def print_to_file__generate_script(code_using_file_opened_for_writing: types.FunctionType,
                                   file_name: str,
                                   global_environment: i.GlobalEnvironmentForPostEdsPhase,
                                   phase_environment: PhaseEnvironmentForScriptGeneration):
    """
    Function that is designed as the execution__generate_script argument to TestCaseSetup, after
    giving the first two arguments using partial application.

    :param code_using_file_opened_for_writing: function: file_variable: str -> ModulesAndStatements
    :param file_name: the name of the file to output to.
    :param global_environment: Environment from act instruction
    :param phase_environment: Environment from act instruction
    """
    file_path = global_environment.eds.act_dir / file_name
    file_name = str(file_path)
    file_var = '_file_var'
    mas = code_using_file_opened_for_writing(file_var)
    all_statements = py.with_opened_file(file_name,
                                         file_var,
                                         'w',
                                         mas.statements)

    program = py.program_lines(mas.used_modules,
                               all_statements)
    phase_environment.append.raw_script_statements(program)


def print_to_file__generate_script2(code_using_file_opened_for_writing: types.FunctionType,
                                    file_name: str):
    """
    Function that is designed as the execution__generate_script argument to TestCaseSetup, after
    giving the first two arguments using partial application.

    :param code_using_file_opened_for_writing: function: file_variable: str -> ModulesAndStatements
    :param file_name: the name of the file to output to.
    :param global_environment: Environment from act instruction
    :param phase_environment: Environment from act instruction
    """
    file_path = pathlib.Path() / file_name
    file_name = str(file_path)
    file_var = '_file_var'
    mas = code_using_file_opened_for_writing(file_var)
    all_statements = py.with_opened_file(file_name,
                                         file_var,
                                         'w',
                                         mas.statements)

    return py.program_lines(mas.used_modules,
                            all_statements)
