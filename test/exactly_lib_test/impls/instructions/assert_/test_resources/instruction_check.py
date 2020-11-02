import os
import unittest
from typing import Sequence

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import pfh, svh
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.impls.types.test_resources.validation import ValidationExpectationSvh, \
    all_validations_passes__svh
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.tcfs.test_resources.ds_construction import tcds_with_act_as_curr_dir__post_act
from exactly_lib_test.test_case.result.test_resources import pfh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ArrangementPostAct2
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
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

    @staticmethod
    def new_w_arbitrary_fs_location(arguments: Arguments) -> 'SourceArrangement':
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
            main_side_effects_on_sds: ValueAssertion[SandboxDs] = asrt.anything_goes(),
            main_side_effects_on_tcds: ValueAssertion[TestCaseDs] = asrt.anything_goes(),
            source: ValueAssertion[ParseSource] = asrt.anything_goes(),
    ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.source = source
        self.symbol_usages = symbol_usages


class ParseExpectation:
    def __init__(
            self,
            source: ValueAssertion[ParseSource] = asrt.anything_goes(),
            symbol_usages: ValueAssertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
    ):
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
            main_side_effects_on_sds: ValueAssertion[SandboxDs] = asrt.anything_goes(),
            main_side_effects_on_tcds: ValueAssertion[TestCaseDs] = asrt.anything_goes(),
    ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_tcds = main_side_effects_on_tcds


class Expectation2:
    def __init__(self,
                 parse: ParseExpectation,
                 execution: ExecutionExpectation,
                 ):
        self.parse = parse
        self.execution = execution


def expectation(
        validation: ValidationExpectationSvh = all_validations_passes__svh(),
        main_result: ValueAssertion[pfh.PassOrFailOrHardError] = pfh_assertions.is_pass(),
        symbol_usages: ValueAssertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
        main_side_effects_on_sds: ValueAssertion[SandboxDs] = asrt.anything_goes(),
        main_side_effects_on_tcds: ValueAssertion[TestCaseDs] = asrt.anything_goes(),
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
    Executor(put, ParserChecker(parser), arrangement, expectation).execute(source)


class Checker:
    def __init__(self, parser: InstructionParser):
        self._parser = parser
        self._parse_checker = ParserChecker(parser)

    def check(self,
              put: unittest.TestCase,
              source: ParseSource,
              arrangement: ArrangementPostAct,
              expectation: Expectation,
              ):
        Executor(put, self._parse_checker, arrangement, expectation).execute(source)

    def check_2(self,
                put: unittest.TestCase,
                source: ParseSource,
                arrangement: ArrangementPostAct2,
                expectation: Expectation2,
                ):
        instruction = self._parse_checker.parse(put,
                                                ARBITRARY_FS_LOCATION_INFO,
                                                source,
                                                expectation.parse,
                                                )
        execution_checker = ExecutionChecker(
            put,
            arrangement,
            expectation.execution,
        )
        execution_checker.check(instruction)

    def check_multi__with_source_variants(
            self,
            put: unittest.TestCase,
            source: SourceArrangement,
            symbol_usages: ValueAssertion[Sequence[SymbolUsage]],
            execution: Sequence[NExArr[ExecutionExpectation, ArrangementPostAct2]],
    ):
        for parse_source in equivalent_source_variants__with_source_check__consume_last_line(put,
                                                                                             source.arguments.as_single_string):
            instruction = self._parse_checker.parse(
                put,
                source.fs_location_info,
                parse_source,
                ParseExpectation(
                    symbol_usages=symbol_usages,
                ))

            for case in execution:
                with put.subTest(execution_case=case.name):
                    checker = ExecutionChecker(put, case.arrangement, case.expected)
                    checker.check(instruction)

    def check_multi(
            self,
            put: unittest.TestCase,
            source: SourceArrangement,
            parse_expectation: ParseExpectation,
            execution: Sequence[NExArr[ExecutionExpectation, ArrangementPostAct2]],
    ):
        parse_source = source.arguments.as_remaining_source
        instruction = self._parse_checker.parse(
            put,
            source.fs_location_info,
            parse_source,
            parse_expectation,
        )

        for case in execution:
            with put.subTest(execution_case=case.name):
                checker = ExecutionChecker(put, case.arrangement, case.expected)
                checker.check(instruction)


class ParserChecker:
    def __init__(self,
                 parser: InstructionParser,
                 ):
        self._parser = parser

    def parse(self,
              put: unittest.TestCase,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource,
              expectation: ParseExpectation,
              ) -> AssertPhaseInstruction:
        instruction = self._parser.parse(fs_location_info, source)

        put.assertIsNotNone(instruction,
                            'Result from parser cannot be None')
        put.assertIsInstance(instruction,
                             AssertPhaseInstruction,
                             'The instruction must be an instance of ' + str(AssertPhaseInstruction))

        assert isinstance(instruction, AssertPhaseInstruction)  # Type info for IDE

        expectation.source.apply_with_message(put, source, 'source after parse')
        expectation.symbol_usages.apply_with_message(put,
                                                     instruction.symbol_usages(),
                                                     'symbol usages after parse')

        return instruction


class Executor:
    def __init__(self,
                 put: unittest.TestCase,
                 parse_checker: ParserChecker,
                 arrangement: ArrangementPostAct,
                 expectation: Expectation):
        self.put = put
        self.parse_checker = parse_checker
        self.arrangement = arrangement
        self.expectation = expectation

    def execute(self, source: ParseSource):
        instruction = self.parse_checker.parse(
            self.put,
            ARBITRARY_FS_LOCATION_INFO,
            source,
            ParseExpectation(
                self.expectation.source,
                self.expectation.symbol_usages,
            ),
        )

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

                environment_builder = InstructionEnvironmentPostSdsBuilder.new_tcds(
                    tcds,
                    self.arrangement.symbols,
                    proc_execution.process_execution_settings,
                )

                environment = environment_builder.build_pre_sds()
                validate_result = self._execute_validate_pre_sds(environment, instruction)
                if not validate_result.is_success:
                    return

            environment = environment_builder.build_post_sds()
            validate_result = self._execute_validate_post_setup(environment, instruction)
            if not validate_result.is_success:
                return

            main_result = self._execute_main(environment, instruction)

            self.expectation.main_side_effects_on_sds.apply(self.put, environment.sds)
            self.expectation.main_side_effects_on_tcds.apply(self.put, tcds)

        self.expectation.main_result.apply(self.put, main_result)

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
        return main_result
