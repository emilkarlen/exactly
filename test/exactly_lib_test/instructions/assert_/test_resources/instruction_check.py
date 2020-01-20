import os
import unittest
from typing import Sequence

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.result import pfh, svh
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.util.file_utils import preserved_cwd
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case.result.test_resources import pfh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ArrangementPostAct2
from exactly_lib_test.test_case_file_structure.test_resources.ds_construction import tcds_with_act_as_curr_dir__post_act
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectationSvh, \
    all_validations_passes__svh
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class SourceArrangement:
    def __init__(self,
                 arguments: Arguments,
                 fs_location_info: FileSystemLocationInfo,
                 ):
        self.arguments = arguments
        self.fs_location_info = fs_location_info


def source_arr_w_arbitrary_fs_location(arguments: Arguments) -> SourceArrangement:
    return SourceArrangement(arguments, ARBITRARY_FS_LOCATION_INFO)


class Expectation:
    def __init__(
            self,
            validation_post_sds: ValueAssertion[svh.SuccessOrValidationErrorOrHardError] =
            svh_assertions.is_success(),

            validation_pre_sds: ValueAssertion[svh.SuccessOrValidationErrorOrHardError] =
            svh_assertions.is_success(),

            main_result: ValueAssertion[pfh.PassOrFailOrHardError] = pfh_assertions.is_pass(),
            symbol_usages: ValueAssertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
            main_side_effects_on_sds: ValueAssertion[SandboxDirectoryStructure] = asrt.anything_goes(),
            main_side_effects_on_tcds: ValueAssertion[Tcds] = asrt.anything_goes(),
            source: ValueAssertion[ParseSource] = asrt.anything_goes(),
    ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.source = source
        self.symbol_usages = symbol_usages


class ExecutionExpectation:
    def __init__(
            self,
            validation_post_sds: ValueAssertion[svh.SuccessOrValidationErrorOrHardError] =
            svh_assertions.is_success(),

            validation_pre_sds: ValueAssertion[svh.SuccessOrValidationErrorOrHardError] =
            svh_assertions.is_success(),

            main_result: ValueAssertion[pfh.PassOrFailOrHardError] = pfh_assertions.is_pass(),
            main_side_effects_on_sds: ValueAssertion[SandboxDirectoryStructure] = asrt.anything_goes(),
            main_side_effects_on_tcds: ValueAssertion[Tcds] = asrt.anything_goes(),
    ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_tcds = main_side_effects_on_tcds


def expectation(
        validation: ValidationExpectationSvh = all_validations_passes__svh(),
        main_result: ValueAssertion[pfh.PassOrFailOrHardError] = pfh_assertions.is_pass(),
        symbol_usages: ValueAssertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
        main_side_effects_on_sds: ValueAssertion[SandboxDirectoryStructure] = asrt.anything_goes(),
        main_side_effects_on_tcds: ValueAssertion[Tcds] = asrt.anything_goes(),
        source: ValueAssertion[ParseSource] = asrt.anything_goes(),
) -> Expectation:
    return Expectation(
        validation_pre_sds=validation.pre_sds,
        validation_post_sds=validation.post_sds,
        main_result=main_result,
        symbol_usages=symbol_usages,
        main_side_effects_on_sds=main_side_effects_on_sds,
        main_side_effects_on_tcds=main_side_effects_on_tcds,
        source=source,
    )


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


class Checker:
    def __init__(self, parser: InstructionParser):
        self._parser = parser

    def check(self,
              put: unittest.TestCase,
              source: ParseSource,
              arrangement: ArrangementPostAct,
              expectation: Expectation,
              ):
        Executor(put, arrangement, expectation).execute(self._parser, source)

    def check_multi__with_source_variants(
            self,
            put: unittest.TestCase,
            source: SourceArrangement,
            symbol_usages: ValueAssertion[Sequence[SymbolUsage]],
            execution: Sequence[NExArr[ExecutionExpectation, ArrangementPostAct2]],
    ):
        for parse_source in equivalent_source_variants__with_source_check(put, source.arguments.as_single_string):
            instruction = self._parser.parse(source.fs_location_info, parse_source)

            put.assertIsNotNone(instruction,
                                'Result from parser cannot be None')
            put.assertIsInstance(instruction,
                                 AssertPhaseInstruction,
                                 'The instruction must be an instance of ' + str(AssertPhaseInstruction))

            assert isinstance(instruction, AssertPhaseInstruction)  # Type info for IDE

            symbol_usages.apply_with_message(put,
                                             instruction.symbol_usages(),
                                             'symbol usages')

            for case in execution:
                with put.subTest(execution_case=case.name):
                    checker = ExecutionChecker(put, case.arrangement, case.expected)
                    checker.check(instruction)


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
        instruction = parser.parse(ARBITRARY_FS_LOCATION_INFO, source)
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

        ex = self.expectation
        exe_checker = ExecutionChecker(self.put,
                                       self.arrangement.as_arrangement_2(),
                                       ExecutionExpectation(
                                           ex.validation_post_sds,
                                           ex.validation_pre_sds,
                                           ex.main_result,
                                           ex.main_side_effects_on_sds,
                                           ex.main_side_effects_on_tcds,
                                       ))
        exe_checker.check(instruction)
        return


class ExecutionChecker:
    def __init__(self,
                 put: unittest.TestCase,
                 arrangement: ArrangementPostAct2,
                 expectation: ExecutionExpectation,
                 ):
        self.put = put
        self.arrangement = arrangement
        self.expectation = expectation

    def check(self, instruction: AssertPhaseInstruction):
        with tcds_with_act_as_curr_dir__post_act(self.arrangement.tcds) as tcds:
            with preserved_cwd():
                os.chdir(str(tcds.hds.case_dir))

                proc_execution = self.arrangement.process_execution
                environment = i.InstructionEnvironmentForPreSdsStep(
                    tcds.hds,
                    environ=proc_execution.process_execution_settings.environ,
                    timeout_in_seconds=proc_execution.process_execution_settings.timeout_in_seconds,
                    symbols=self.arrangement.symbols,
                )
                validate_result = self._execute_validate_pre_sds(environment, instruction)
                if not validate_result.is_success:
                    return

            environment = i.InstructionEnvironmentForPostSdsStep(
                environment.hds,
                environment.environ,
                tcds.sds,
                phase_identifier.ASSERT.identifier,
                timeout_in_seconds=proc_execution.process_execution_settings.timeout_in_seconds,
                symbols=self.arrangement.symbols,
            )
            validate_result = self._execute_validate_post_setup(environment, instruction)
            if not validate_result.is_success:
                return

            self._execute_main(environment, instruction)

            self.expectation.main_side_effects_on_sds.apply(self.put, environment.sds)
            self.expectation.main_side_effects_on_tcds.apply(self.put, tcds)

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
        main_result = instruction.main(environment, self.arrangement.process_execution.os_services)
        self.put.assertIsNotNone(main_result,
                                 'Result from main method cannot be None')
        self.expectation.main_result.apply(self.put, main_result)
        return main_result
