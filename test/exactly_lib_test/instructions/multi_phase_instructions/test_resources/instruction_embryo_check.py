import unittest

from exactly_lib.execution.phase_step_identifiers import phase_step
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_embryo import InstructionEmbryoParser, \
    InstructionEmbryo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols import home_and_sds_utils
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class PostActionCheck:
    def apply(self,
              put: unittest.TestCase,
              home_and_sds: HomeAndSds):
        pass


class Expectation:
    def __init__(self,
                 validation_pre_sds: asrt.ValueAssertion = asrt.is_none,
                 validation_post_sds: asrt.ValueAssertion = asrt.is_none,
                 main_result: asrt.ValueAssertion = asrt.anything_goes(),
                 symbol_usages: asrt.ValueAssertion = asrt.is_empty_list,
                 main_side_effects_on_sds: asrt.ValueAssertion = asrt.anything_goes(),
                 side_effects_on_home_and_sds: asrt.ValueAssertion = asrt.anything_goes(),
                 side_effects_on_home: asrt.ValueAssertion = asrt.anything_goes(),
                 source: asrt.ValueAssertion = asrt.anything_goes(),
                 main_side_effect_on_environment_variables: asrt.ValueAssertion = asrt.anything_goes(),
                 ):
        self.validation_pre_sds = validation_pre_sds
        self.validation_post_sds = validation_post_sds
        self.main_result = main_result
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.side_effects_on_home_and_sds = side_effects_on_home_and_sds
        self.side_effects_on_home = side_effects_on_home
        self.source = source
        self.symbol_usages = symbol_usages
        self.main_side_effect_on_environment_variables = main_side_effect_on_environment_variables


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: InstructionEmbryoParser,
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: Expectation):
        check(self,
              parser,
              source,
              arrangement,
              expectation)


def check(put: unittest.TestCase,
          parser: InstructionEmbryoParser,
          source: ParseSource,
          arrangement: ArrangementWithSds,
          expectation: Expectation):
    Executor(put, arrangement, expectation).execute(parser, source)


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementWithSds,
                 expectation: Expectation):
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation
        self.message_builder = asrt.MessageBuilder()

    def execute(self,
                parser: InstructionEmbryoParser,
                source: ParseSource):
        instruction = parser.parse(source)
        asrt.is_instance(InstructionEmbryo).apply_with_message(self.put, instruction,
                                                               'Instruction class')
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(instruction, InstructionEmbryo)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          instruction.symbol_usages,
                                                          'symbol-usages after parse')
        with home_and_sds_utils.home_and_sds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_home_contents=self.arrangement.non_home_contents,
                home_or_sds_contents=self.arrangement.home_or_sds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:
            home_and_sds = path_resolving_environment.home_and_sds
            self.arrangement.post_sds_population_action.apply(path_resolving_environment)
            environment = InstructionEnvironmentForPreSdsStep(home_and_sds.hds,
                                                              _initial_environment_variables_dict(self.arrangement),
                                                              symbols=self.arrangement.symbols)
            validate_result = self._execute_validate_pre_sds(environment, instruction)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_PRE_SDS)
            if validate_result is not None:
                return
            environment = InstructionEnvironmentForPostSdsStep(
                environment.hds,
                environment.environ,
                home_and_sds.sds,
                'phase_identifier_for_unknown_phase',
                timeout_in_seconds=self.arrangement.process_execution_settings.timeout_in_seconds,
                symbols=self.arrangement.symbols)
            validate_result = self._execute_validate_post_setup(environment, instruction)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            if validate_result is not None:
                return

            self._execute_main(environment, instruction)
            self.expectation.main_side_effects_on_sds.apply_with_message(self.put, home_and_sds.sds,
                                                                         'side_effects_on_files')
            self.expectation.side_effects_on_home_and_sds.apply_with_message(self.put, home_and_sds,
                                                                             'side_effects_on_home_and_sds')
            self.expectation.main_side_effect_on_environment_variables.apply_with_message(
                self.put,
                environment.environ,
                'main side effects on environment variables')
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages,
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)
            self.expectation.side_effects_on_home.apply_with_message(self.put, home_and_sds.hds.case_dir,
                                                                     'side_effects_on_home')

    def _execute_validate_pre_sds(
            self,
            environment: InstructionEnvironmentForPreSdsStep,
            instruction: InstructionEmbryo) -> str:
        result = instruction.validator.validate_pre_sds_if_applicable(environment.path_resolving_environment)
        self.expectation.validation_pre_sds.apply_with_message(self.put, result,
                                                               'validation_pre_sds')
        return result

    def _execute_validate_post_setup(
            self,
            environment: InstructionEnvironmentForPostSdsStep,
            instruction: InstructionEmbryo) -> str:
        result = instruction.validator.validate_post_sds_if_applicable(environment.path_resolving_environment)
        self.expectation.validation_post_sds.apply_with_message(self.put, result,
                                                                'validation_post_sds')
        return result

    def _execute_main(self,
                      environment: InstructionEnvironmentForPostSdsStep,
                      instruction: InstructionEmbryo):
        result = instruction.main(environment,
                                  environment.phase_logging,
                                  self.arrangement.os_services)
        self.expectation.main_result.apply_with_message(self.put, result,
                                                        'result from main')


def _initial_environment_variables_dict(arrangement: ArrangementWithSds) -> dict:
    environ = arrangement.process_execution_settings.environ
    if environ is None:
        environ = {}
    return environ
