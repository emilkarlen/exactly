import types
import unittest

from exactly_lib.instructions.multi_phase_instructions.utils import instruction_parts
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_parts import InstructionParts, \
    InstructionPartsParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.symbol.restrictions.concrete_restrictions import ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.restrictions.value_restrictions import StringRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, PhaseLoggingPaths
from exactly_lib.test_case.phases.result import pfh, sh
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.instructions.test_resources.pre_or_post_sds_validator import ValidatorThat
from exactly_lib_test.section_document.test_resources.instruction_parser import ParserThatGives
from exactly_lib_test.symbol.test_resources.concrete_restriction_assertion import \
    equals_string_restriction
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import \
    equals_symbol_reference_with_restriction_on_direct_target
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Configuration(ConfigurationBase):
    def new_instruction_from_parts(self, parts: InstructionParts):
        raise NotImplementedError()

    def step_sequence_of_successful_execution(self) -> list:
        raise NotImplementedError()

    def instruction_parser_from_parts_parser(self, parts_parser: InstructionPartsParser) -> InstructionParser:
        raise NotImplementedError()


def suite_for(conf: Configuration) -> unittest.TestSuite:
    test_case_classes = [
        TestStepSequenceOfSuccessfulExecutionOfHardCodedInstruction,
        TestStepSequenceOfSuccessfulExecutionOfInstructionFromParser,

        TestSymbolUsagesOfHardCodedInstruction,
        TestSymbolUsagesOfInstructionFromParser,

        TestFailureOfValidatePreSdsOfInstructionFromParser,
        TestFailureOfValidatePostSetupOfInstructionFromParser,
        TestFailureOfMainOfInstructionFromParser,
    ]
    suites = [test_case_class(conf)
              for test_case_class in test_case_classes]
    return unittest.TestSuite(suites)


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: Configuration):
        super().__init__()
        self.conf = conf

    def runTest(self):
        raise NotImplementedError()

    def shortDescription(self):
        return str(type(self)) + '\n/ ' + str(type(self.conf))


class TestStepSequenceOfSuccessfulExecutionOfHardCodedInstruction(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        actual_recordings = []
        parts = instruction_parts_that_records_execution_steps(actual_recordings)
        instruction = self.conf.new_instruction_from_parts(parts)
        hard_coded_parser = ParserThatGives(instruction)
        source = remaining_source('ignored')
        # ACT & ASSERT #
        self.conf.run_test_with_parser(self,
                                       hard_coded_parser,
                                       source,
                                       self.conf.arrangement(),
                                       self.conf.expect_success())
        self.assertEqual(self.conf.step_sequence_of_successful_execution(),
                         actual_recordings,
                         'sequence of invocations on instruction from InstructionPart')


class TestStepSequenceOfSuccessfulExecutionOfInstructionFromParser(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        actual_recordings = []
        parts = instruction_parts_that_records_execution_steps(actual_recordings)
        parser = self.conf.instruction_parser_from_parts_parser(PartsParserThatGives(parts))
        source = remaining_source('ignored')
        # ACT & ASSERT #
        self.conf.run_test_with_parser(self,
                                       parser,
                                       source,
                                       self.conf.arrangement(),
                                       self.conf.expect_success())
        self.assertEqual(self.conf.step_sequence_of_successful_execution(),
                         actual_recordings,
                         'sequence of invocations on instruction from InstructionPart')


class TestSymbolUsagesOfHardCodedInstruction(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        symbol_name = 'SYMBOL_NAME'
        string_restriction = StringRestriction()
        symbol_reference = SymbolReference(symbol_name, ReferenceRestrictionsOnDirectAndIndirect(string_restriction))
        expected_symbol_usages = asrt.matches_sequence([
            equals_symbol_reference_with_restriction_on_direct_target(
                symbol_name,
                equals_string_restriction(string_restriction))
        ])
        parts = instruction_parts.InstructionParts(ValidatorThat(),
                                                   MainStepExecutorThat(),
                                                   symbol_usages=(symbol_reference,))
        instruction = self.conf.new_instruction_from_parts(parts)
        hard_coded_parser = ParserThatGives(instruction)
        source = remaining_source('ignored')
        # ACT & ASSERT #
        self.conf.run_test_with_parser(self,
                                       hard_coded_parser,
                                       source,
                                       self.conf.arrangement(),
                                       self.conf.expect_success(symbol_usages=expected_symbol_usages))


class TestSymbolUsagesOfInstructionFromParser(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        symbol_name = 'SYMBOL_NAME'
        string_restriction = StringRestriction()
        symbol_reference = SymbolReference(symbol_name, ReferenceRestrictionsOnDirectAndIndirect(string_restriction))
        expected_symbol_usages = asrt.matches_sequence([
            equals_symbol_reference_with_restriction_on_direct_target(
                symbol_name,
                equals_string_restriction(string_restriction))
        ])
        parts = instruction_parts.InstructionParts(ValidatorThat(),
                                                   MainStepExecutorThat(),
                                                   symbol_usages=(symbol_reference,))
        parser = self.conf.instruction_parser_from_parts_parser(PartsParserThatGives(parts))
        source = remaining_source('ignored')
        # ACT & ASSERT #
        self.conf.run_test_with_parser(self,
                                       parser,
                                       source,
                                       self.conf.arrangement(),
                                       self.conf.expect_success(symbol_usages=expected_symbol_usages))


class TestFailureOfValidatePreSdsOfInstructionFromParser(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        the_error_message = 'the error message'
        parts = instruction_parts.InstructionParts(
            ValidatorThat(pre_sds_return_value=the_error_message),
            MainStepExecutorThat())
        parser = self.conf.instruction_parser_from_parts_parser(PartsParserThatGives(parts))
        source = remaining_source('ignored')
        # ACT & ASSERT #
        self.conf.run_test_with_parser(self,
                                       parser,
                                       source,
                                       self.conf.arrangement(),
                                       self.conf.expect_failing_validation_pre_sds(
                                           assertion_on_error_message=asrt.equals(the_error_message)
                                       ))


class TestFailureOfValidatePostSetupOfInstructionFromParser(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        the_error_message = 'the error message'
        parts = instruction_parts.InstructionParts(
            ValidatorThat(post_setup_return_value=the_error_message),
            MainStepExecutorThat())
        parser = self.conf.instruction_parser_from_parts_parser(PartsParserThatGives(parts))
        source = remaining_source('ignored')
        # ACT & ASSERT #
        self.conf.run_test_with_parser(self,
                                       parser,
                                       source,
                                       self.conf.arrangement(),
                                       self.conf.expect_failing_validation_post_setup(
                                           assertion_on_error_message=asrt.equals(the_error_message)
                                       ))


class TestFailureOfMainOfInstructionFromParser(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        the_error_message = 'the error message'
        parts = instruction_parts.InstructionParts(
            ValidatorThat(),
            MainStepExecutorThat(assertion_return_value=pfh.new_pfh_fail(the_error_message),
                                 non_assertion_return_value=sh.new_sh_hard_error(the_error_message)))
        parser = self.conf.instruction_parser_from_parts_parser(PartsParserThatGives(parts))
        source = remaining_source('ignored')
        # ACT & ASSERT #
        self.conf.run_test_with_parser(self,
                                       parser,
                                       source,
                                       self.conf.arrangement(),
                                       self.conf.expect_failure_of_main(
                                           assertion_on_error_message=asrt.equals(the_error_message)
                                       ))


def instruction_parts_that_records_execution_steps(recorder: list) -> instruction_parts.InstructionParts:
    return instruction_parts.InstructionParts(
        ValidatorThat(
            pre_sds_action=record_value(recorder,
                                        VALIDATE_STEP_PRE_SDS_IF_APPLICABLE),
            post_setup_action=record_value(recorder,
                                           VALIDATE_STEP_POST_SETUP_IF_APPLICABLE)),
        MainStepExecutorThat(
            assertion_action=record_value(recorder,
                                          MAIN_STEP_AS_ASSERTION),
            non_assertion_action=record_value(recorder,
                                              MAIN_STEP_AS_NON_ASSERTION)))


def do_nothing(*args, **kwargs):
    pass


class MainStepExecutorThat(instruction_parts.MainStepExecutor):
    def __init__(self,
                 assertion_action=do_nothing,
                 assertion_return_value=pfh.new_pfh_pass(),
                 non_assertion_action=do_nothing,
                 non_assertion_return_value=sh.new_sh_success(),

                 ):
        self.non_assertion_return_value = non_assertion_return_value
        self.non_assertion_action = non_assertion_action
        self.assertion_return_value = assertion_return_value
        self.assertion_action = assertion_action

    def apply_as_assertion(self,
                           environment: InstructionEnvironmentForPostSdsStep,
                           logging_paths: PhaseLoggingPaths,
                           os_services: OsServices) -> pfh.PassOrFailOrHardError:
        self.assertion_action(environment, logging_paths, os_services)
        return self.assertion_return_value

    def apply_as_non_assertion(self,
                               environment: InstructionEnvironmentForPostSdsStep,
                               logging_paths: PhaseLoggingPaths,
                               os_services: OsServices) -> sh.SuccessOrHardError:
        self.non_assertion_action(environment, logging_paths, os_services)
        return self.non_assertion_return_value


MAIN_STEP_AS_ASSERTION = 'apply_as_assertion'
MAIN_STEP_AS_NON_ASSERTION = 'apply_as_non_assertion'
VALIDATE_STEP_PRE_SDS_IF_APPLICABLE = 'validate_pre_sds_if_applicable'
VALIDATE_STEP_POST_SETUP_IF_APPLICABLE = 'validate_post_sds_if_applicable'


def record_value(recorder: list, value_to_record) -> types.FunctionType:
    def ret_val(*args, **kwargs):
        recorder.append(value_to_record)

    return ret_val


class RecordingAction:
    def __init__(self, recorder: list):
        """

        :type recorder: object
        """


class PartsParserThatGives(InstructionPartsParser):
    def __init__(self, parts: instruction_parts.InstructionParts):
        self.parts = parts

    def parse(self, source: ParseSource) -> InstructionParts:
        return self.parts
