import os
import unittest
from typing import Sequence

from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.model import Instruction
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.result import pfh, svh
from exactly_lib.util.file_utils.misc_utils import preserved_cwd
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc, text_doc_assertions
from exactly_lib_test.impls.instructions.test_resources.instr_arr_exp import ParseExpectation
from exactly_lib_test.impls.instructions.test_resources.instruction_checker import InstructionChecker
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.impls.test_resources.validation.validation import ValidationActual
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line, \
    equivalent_source_variants__consume_last_line__s__nsc
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source_of_abs_stx
from exactly_lib_test.tcfs.test_resources.ds_construction import tcds_with_act_as_curr_dir__post_act
from exactly_lib_test.test_case.result.test_resources import pfh_assertions, svh_assertions
from exactly_lib_test.test_case.test_resources import instruction_settings as instr_settings
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct, ArrangementPostAct2
from exactly_lib_test.test_case.test_resources.instruction_environment import InstructionEnvironmentPostSdsBuilder
from exactly_lib_test.test_resources.source import layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, StopAssertion


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
            validation_post_sds: Assertion[svh.SuccessOrValidationErrorOrHardError] =
            svh_assertions.is_success(),

            validation_pre_sds: Assertion[svh.SuccessOrValidationErrorOrHardError] =
            svh_assertions.is_success(),

            main_result: Assertion[pfh.PassOrFailOrHardError] = pfh_assertions.is_pass(),
            symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
            main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
            main_side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
            source: Assertion[ParseSource] = asrt.anything_goes(),
            main_raises_hard_error: bool = False,
            proc_exe_settings: Assertion[ProcessExecutionSettings]
            = asrt.is_instance(ProcessExecutionSettings),
            instruction_settings: Assertion[InstructionSettings]
            = asrt.is_instance(InstructionSettings)
    ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.main_raises_hard_error = main_raises_hard_error
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.source = source
        self.symbol_usages = symbol_usages
        self.proc_exe_settings = proc_exe_settings
        self.instruction_settings = instruction_settings


class ExecutionExpectation:
    def __init__(
            self,
            validation_post_sds: Assertion[svh.SuccessOrValidationErrorOrHardError] =
            svh_assertions.is_success(),

            validation_pre_sds: Assertion[svh.SuccessOrValidationErrorOrHardError] =
            svh_assertions.is_success(),

            main_result: Assertion[pfh.PassOrFailOrHardError] = pfh_assertions.is_pass(),
            main_raises_hard_error: bool = False,
            main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
            main_side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
            proc_exe_settings: Assertion[ProcessExecutionSettings]
            = asrt.is_instance(ProcessExecutionSettings),
            instruction_settings: Assertion[InstructionSettings]
            = asrt.is_instance(InstructionSettings)
    ):
        self.validation_post_sds = validation_post_sds
        self.validation_pre_sds = validation_pre_sds
        self.main_result = main_result
        self.main_raises_hard_error = main_raises_hard_error
        self.main_side_effects_on_sds = main_side_effects_on_sds
        self.main_side_effects_on_tcds = main_side_effects_on_tcds
        self.proc_exe_settings = proc_exe_settings
        self.instruction_settings = instruction_settings

    @staticmethod
    def of_validation(expectation_: ValidationExpectationSvh) -> 'ExecutionExpectation':
        return ExecutionExpectation(
            validation_pre_sds=expectation_.pre_sds,
            validation_post_sds=expectation_.post_sds,
        )

    @staticmethod
    def validation_corresponding_to__post_sds_as_hard_error(actual: ValidationActual) -> 'ExecutionExpectation':
        if actual.pre_sds is not None:
            return ExecutionExpectation(
                validation_pre_sds=svh_assertions.is_validation_error(
                    asrt_text_doc.is_string_for_test_that_equals(actual.pre_sds),
                )
            )
        elif actual.post_sds is not None:
            return ExecutionExpectation(
                main_result=pfh_assertions.is_hard_error(
                    asrt_text_doc.is_string_for_test_that_equals(actual.post_sds),
                )
            )
        else:
            return ExecutionExpectation()

    @staticmethod
    def validation_corresponding_to_dsp__post_sds_as_hard_error(path_location: DirectoryStructurePartition
                                                                ) -> 'ExecutionExpectation':
        if path_location is DirectoryStructurePartition.HDS:
            return ExecutionExpectation(
                validation_pre_sds=svh_assertions.is_validation_error()
            )
        else:
            return ExecutionExpectation(
                main_result=pfh_assertions.is_hard_error()
            )


class Expectation2:
    def __init__(self,
                 parse: ParseExpectation = ParseExpectation(),
                 execution: ExecutionExpectation = ExecutionExpectation(),
                 ):
        self.parse = parse
        self.execution = execution


class MultiSourceExpectation:
    def __init__(self,
                 symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
                 execution: ExecutionExpectation = ExecutionExpectation(),
                 ):
        self.symbol_usages = symbol_usages
        self.execution = execution


def expectation(
        validation: ValidationExpectationSvh = ValidationExpectationSvh.passes(),
        main_result: Assertion[pfh.PassOrFailOrHardError] = pfh_assertions.is_pass(),
        symbol_usages: Assertion[Sequence[SymbolUsage]] = asrt.is_empty_sequence,
        main_side_effects_on_sds: Assertion[SandboxDs] = asrt.anything_goes(),
        main_side_effects_on_tcds: Assertion[TestCaseDs] = asrt.anything_goes(),
        source: Assertion[ParseSource] = asrt.anything_goes(),
        instruction_settings: Assertion[InstructionSettings]
        = asrt.is_instance(InstructionSettings)
) -> Expectation:
    return Expectation(
        validation_pre_sds=validation.pre_sds,
        validation_post_sds=validation.post_sds,
        main_result=main_result,
        symbol_usages=symbol_usages,
        main_side_effects_on_sds=main_side_effects_on_sds,
        main_side_effects_on_tcds=main_side_effects_on_tcds,
        instruction_settings=instruction_settings,
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

    def check__abs_stx(self,
                       put: unittest.TestCase,
                       syntax: AbstractSyntax,
                       arrangement: ArrangementPostAct2,
                       expectation: Expectation2,
                       ):
        self.check_2(
            put,
            remaining_source_of_abs_stx(syntax),
            arrangement,
            expectation,
        )

    def check__abs_stx__source_variants(self,
                                        put: unittest.TestCase,
                                        syntax: AbstractSyntax,
                                        arrangement: ArrangementPostAct2,
                                        expectation: MultiSourceExpectation,
                                        ):
        tokens = syntax.tokenization()
        for layout_case in layout.STANDARD_LAYOUT_SPECS:
            source_str = tokens.layout(layout_case.value)
            for source_case in equivalent_source_variants__consume_last_line__s__nsc(source_str):
                with put.subTest(layout=layout_case.name,
                                 source_variant=source_case.name):
                    self.check_2(
                        put,
                        source_case.source,
                        arrangement,
                        Expectation2(
                            ParseExpectation(
                                source_case.expectation,
                                expectation.symbol_usages,
                            ),
                            expectation.execution,
                        )
                    )

    def check_multi__with_source_variants(
            self,
            put: unittest.TestCase,
            source: SourceArrangement,
            symbol_usages: Assertion[Sequence[SymbolUsage]],
            execution: Sequence[NExArr[ExecutionExpectation, ArrangementPostAct2]],
    ):
        for parse_source in equivalent_source_variants__with_source_check__consume_last_line(
                put,
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
                                           ex.main_raises_hard_error,
                                           ex.main_side_effects_on_sds,
                                           ex.main_side_effects_on_tcds,
                                           ex.proc_exe_settings,
                                           ex.instruction_settings,
                                       ))
        exe_checker.check(instruction)
        return


class AssertInstructionChecker(InstructionChecker[ArrangementPostAct2, ExecutionExpectation]):
    def check(self,
              put: unittest.TestCase,
              instruction: Instruction,
              arrangement: ArrangementPostAct,
              expectation: ExecutionExpectation):
        put.assertIsInstance(instruction, AssertPhaseInstruction, 'instruction type')
        assert isinstance(instruction, AssertPhaseInstruction)  # Type info for IDE

        ExecutionChecker(put, arrangement.as_arrangement_2(), expectation).check(instruction)


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

            instruction_settings = instr_settings.from_proc_exe_settings(
                self.arrangement.process_execution.process_execution_settings,
                self.arrangement.default_environ_getter,
            )

            try:
                main_result = self._execute_main(environment, instruction_settings, instruction)
            except StopAssertion:
                return

            self.expectation.instruction_settings.apply_with_message(self.put, instruction_settings,
                                                                     'instruction settings')
            self.expectation.proc_exe_settings.apply_with_message(self.put, environment.proc_exe_settings,
                                                                  'proc exe settings')
            self.expectation.main_side_effects_on_sds.apply_with_message(self.put, environment.sds, 'SDS')
            self.expectation.main_side_effects_on_tcds.apply_with_message(self.put, tcds, 'TCDS')

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
                      settings: InstructionSettings,
                      instruction: AssertPhaseInstruction) -> pfh.PassOrFailOrHardError:
        try:
            main_result = instruction.main(environment,
                                           settings,
                                           self.arrangement.process_execution.os_services)
            self.put.assertIsNotNone(main_result,
                                     'Result from main method cannot be None')
        except HardErrorException as ex:
            if self.expectation.main_raises_hard_error:
                text_doc_assertions.assert_is_valid_text_renderer(self.put, ex.error)
                raise StopAssertion()
            else:
                self.put.fail('unexpected {} from main'.format(HardErrorException))

        if self.expectation.main_raises_hard_error:
            self.put.fail('main does not raise ' + str(HardErrorException))

        return main_result
