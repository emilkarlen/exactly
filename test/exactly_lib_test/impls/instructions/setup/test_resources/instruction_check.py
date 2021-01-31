import os
import unittest
from typing import Sequence, Optional

from exactly_lib.execution import phase_step
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup.instruction import SetupPhaseInstruction
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.result import sh, svh
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings, with_no_timeout
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.partial_execution.test_resources import settings_handlers
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__consume_last_line__s__nsc
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.tcfs.test_resources import non_hds_populator, hds_populators, \
    tcds_populators, sds_populator
from exactly_lib_test.test_case.result.test_resources import sh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources import settings_builder_assertions as asrt_settings
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_case.test_resources.settings_builder_assertions import SettingsBuilderAssertionModel
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction, tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class Arrangement(ArrangementWithSds):
    def __init__(self,
                 pre_contents_population_action: TcdsAction = TcdsAction(),
                 hds_contents: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents_before_main: sds_populator.SdsPopulator = sds_populator.empty(),
                 non_hds_contents: non_hds_populator.NonHdsPopulator = non_hds_populator.empty(),
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 os_services: OsServices = os_services_access.new_for_current_os(),
                 process_execution_settings: ProcessExecutionSettings = with_no_timeout(),
                 settings_builder: Optional[SetupSettingsBuilder] = None,
                 symbols: SymbolTable = None,
                 fs_location_info: FileSystemLocationInfo = ARBITRARY_FS_LOCATION_INFO,
                 ):
        super().__init__(pre_contents_population_action=pre_contents_population_action,
                         hds_contents=hds_contents,
                         sds_contents=sds_contents_before_main,
                         non_hds_contents=non_hds_contents,
                         tcds_contents=tcds_contents,
                         os_services=os_services,
                         process_execution_settings=process_execution_settings,
                         symbols=symbols,
                         fs_location_info=fs_location_info,
                         )
        self.initial_settings_builder = settings_handlers.builder_from_optional(settings_builder)


class Expectation:
    """
    Expectation on properties of the execution of an instruction.
    
    Default settings: successful steps execution and NO symbol usages.
    """

    def __init__(self,
                 pre_validation_result: Assertion[svh.SuccessOrValidationErrorOrHardError]
                 = svh_assertions.is_success(),
                 main_result: Assertion[sh.SuccessOrHardError]
                 = sh_assertions.is_success(),
                 post_validation_result: Assertion[svh.SuccessOrValidationErrorOrHardError]
                 = svh_assertions.is_success(),
                 symbol_usages: Assertion[Sequence[SymbolUsage]]
                 = asrt.is_empty_sequence,
                 main_side_effects_on_sds: Assertion[SandboxDs]
                 = asrt.anything_goes(),
                 main_side_effects_on_tcds: Assertion[TestCaseDs]
                 = asrt.anything_goes(),
                 settings_builder: Assertion[SettingsBuilderAssertionModel]
                 = asrt_settings.stdin_is_not_present(),
                 source: Assertion[ParseSource]
                 = asrt.anything_goes(),
                 symbols_after_main: Assertion[Sequence[SymbolUsage]]
                 = asrt.anything_goes(),
                 ):
        self.pre_validation_result = pre_validation_result
        self.post_validation_result = post_validation_result
        self.main_result = main_result
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.settings_builder = settings_builder
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.source = source
        self.symbol_usages = symbol_usages
        self.symbols_after_main = symbols_after_main


class MultiSourceExpectation:
    """
    Expectation on properties of the execution of an instruction.

    Default settings: successful steps execution and NO symbol usages.
    """

    def __init__(self,
                 validation: ValidationExpectationSvh
                 = ValidationExpectationSvh.passes(),
                 main_result: Assertion[sh.SuccessOrHardError]
                 = sh_assertions.is_success(),
                 symbols_after_parse: Assertion[Sequence[SymbolUsage]]
                 = asrt.is_empty_sequence,
                 main_side_effects_on_sds: Assertion[SandboxDs]
                 = asrt.anything_goes(),
                 main_side_effects_on_tcds: Assertion[TestCaseDs]
                 = asrt.anything_goes(),
                 settings_builder: Assertion[SettingsBuilderAssertionModel]
                 = asrt_settings.stdin_is_not_present(),
                 symbols_after_main: Assertion[Sequence[SymbolUsage]]
                 = asrt.anything_goes(),
                 ):
        self.validation = validation
        self.main_result = main_result
        self.settings_builder = settings_builder
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.symbols_after_parse = symbols_after_parse
        self.symbols_after_main = symbols_after_main

    def as_expectation_w_source(self, source: Assertion[ParseSource] = asrt.anything_goes()) -> Expectation:
        return Expectation(
            self.validation.pre_sds,
            self.main_result,
            self.validation.post_sds,
            self.symbols_after_parse,
            self.main_side_effects_on_sds,
            self.main_side_effects_on_tcds,
            self.settings_builder,
            source,
            self.symbols_after_main,
        )


is_success = Expectation


class TestCaseBase(unittest.TestCase):
    def _check(self,
               parser: InstructionParser,
               source: ParseSource,
               arrangement: Arrangement,
               expectation: Expectation):
        check(self, parser, source, arrangement, expectation)


def check(put: unittest.TestCase,
          parser: InstructionParser,
          source: ParseSource,
          arrangement: Arrangement,
          expectation: Expectation):
    Executor(put, arrangement, expectation).execute(parser, source)


class Checker:
    def __init__(self, parser: InstructionParser):
        self._parser = parser

    def check(self,
              put: unittest.TestCase,
              source: ParseSource,
              arrangement: Arrangement,
              expectation: Expectation,
              ):
        Executor(put, arrangement, expectation).execute(self._parser, source)

    def check_multi_source__abs_stx(self,
                                    put: unittest.TestCase,
                                    source: AbstractSyntax,
                                    arrangement: Arrangement,
                                    expectation: MultiSourceExpectation,
                                    ):
        tokens = source.tokenization()
        for layout_case in layout.STANDARD_LAYOUT_SPECS:
            source_str = tokens.layout(layout_case.value)
            for source_case in equivalent_source_variants__consume_last_line__s__nsc(source_str):
                with put.subTest(layout=layout_case.name,
                                 source_variant=source_case.name):
                    self.check(put,
                               source_case.source,
                               arrangement,
                               expectation.as_expectation_w_source(source_case.expectation),
                               )


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
        instruction = parser.parse(self.arrangement.fs_location_info, source)
        self.put.assertIsNotNone(instruction,
                                 'Result from parser cannot be None')
        self.put.assertIsInstance(instruction,
                                  SetupPhaseInstruction,
                                  'The instruction must be an instance of ' + str(SetupPhaseInstruction))
        self.expectation.source.apply_with_message(self.put, source, 'source')
        assert isinstance(instruction, SetupPhaseInstruction)
        self.expectation.symbol_usages.apply_with_message(self.put,
                                                          instruction.symbol_usages(),
                                                          'symbol-usages after parse')
        self.expectation.symbol_usages.apply_with_message(self.put, instruction.symbol_usages(),
                                                          'symbol-usages')

        with tcds_with_act_as_curr_dir(
                pre_contents_population_action=self.arrangement.pre_contents_population_action,
                hds_contents=self.arrangement.hds_contents,
                sds_contents=self.arrangement.sds_contents,
                non_hds_contents=self.arrangement.non_hds_contents,
                tcds_contents=self.arrangement.tcds_contents,
                symbols=self.arrangement.symbols) as path_resolving_environment:

            self.arrangement.post_sds_population_action.apply(path_resolving_environment)

            environment_builder = InstructionEnvironmentPostSdsBuilder.new_tcds(
                path_resolving_environment.tcds,
                self.arrangement.symbols,
                self.arrangement.process_execution_settings,
            )

            with preserved_cwd():
                os.chdir(str(path_resolving_environment.hds.case_dir))

                environment = environment_builder.build_pre_sds()
                pre_validate_result = self._execute_pre_validate(environment, instruction)
                self.expectation.symbol_usages.apply_with_message(self.put,
                                                                  instruction.symbol_usages(),
                                                                  'symbol-usages after ' +
                                                                  phase_step.STEP__VALIDATE_PRE_SDS)
                if not pre_validate_result.is_success:
                    return

            instruction_environment = environment_builder.build_post_sds()

            tcds = path_resolving_environment.tcds
            sds = tcds.sds

            main_result = self._execute_main(instruction_environment, instruction)

            self.expectation.main_side_effects_on_sds.apply(self.put, sds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__MAIN)
            if not main_result.is_success:
                return
            self.expectation.symbols_after_main.apply_with_message(
                self.put,
                instruction_environment.symbols,
                'symbols_after_main')
            self._execute_post_validate(instruction_environment, instruction)
            self.expectation.main_side_effects_on_tcds.apply(self.put,
                                                             instruction_environment.tcds)
            self.expectation.symbol_usages.apply_with_message(self.put,
                                                              instruction.symbol_usages(),
                                                              'symbol-usages after ' +
                                                              phase_step.STEP__VALIDATE_POST_SETUP)
            self.expectation.settings_builder.apply_with_message(
                self.put,
                SettingsBuilderAssertionModel(self.arrangement.initial_settings_builder,
                                              instruction_environment,
                                              self.arrangement.os_services),
                'settings builder'
            )
        self.expectation.main_result.apply_with_message(self.put, main_result,
                                                        'main-result (wo access to TCDS)')

    def _execute_pre_validate(self,
                              environment: InstructionEnvironmentForPreSdsStep,
                              instruction: SetupPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        pre_validate_result = instruction.validate_pre_sds(environment)
        self.put.assertIsInstance(pre_validate_result,
                                  svh.SuccessOrValidationErrorOrHardError,
                                  'pre_validate must return a ' + str(svh.SuccessOrValidationErrorOrHardError))
        self.put.assertIsNotNone(pre_validate_result,
                                 'Result from pre_validate method cannot be None')
        self.expectation.pre_validation_result.apply(self.put, pre_validate_result)
        return pre_validate_result

    def _execute_main(self,
                      instruction_environment: InstructionEnvironmentForPostSdsStep,
                      instruction: SetupPhaseInstruction) -> sh.SuccessOrHardError:
        settings_builder = self.arrangement.initial_settings_builder
        main_result = instruction.main(instruction_environment,
                                       self.arrangement.os_services,
                                       settings_builder)
        self.put.assertIsInstance(main_result,
                                  sh.SuccessOrHardError,
                                  'main must return a ' + str(sh.SuccessOrHardError))
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        return main_result

    def _execute_post_validate(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               instruction: SetupPhaseInstruction) -> svh.SuccessOrValidationErrorOrHardError:
        post_validate_result = instruction.validate_post_setup(environment)
        self.put.assertIsInstance(post_validate_result,
                                  svh.SuccessOrValidationErrorOrHardError,
                                  'post_validate must return a ' + str(svh.SuccessOrValidationErrorOrHardError))
        self.put.assertIsNotNone(post_validate_result,
                                 'Result from post_validate method cannot be None')
        self.expectation.post_validation_result.apply(self.put, post_validate_result)
        return post_validate_result
