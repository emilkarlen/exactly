import unittest

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output import \
    arguments_building as po_ab
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output import \
    configuration
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output.configuration import \
    TestCaseBase
from exactly_lib_test.instructions.assert_.test_resources.stdout_stderr.program_output.utils import matches_reference
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    is_any_data_type_reference_restrictions
from exactly_lib_test.symbol.test_resources.arguments_building import SymbolReferenceArgument
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_case.result.test_resources import svh_assertions as asrt_svh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import matcher_arguments
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(conf: configuration.ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSymbolReferences(conf),
        TestFailingValidationPreSds(conf),
        TestFailingValidationPostSds(conf),
    ])


class TestSymbolReferences(TestCaseBase):
    def runTest(self):
        # ARRANGE #

        symbol_in_program_source = NameAndValue('SYMBOL_IN_PROGRAM_SOURCE',
                                                is_any_data_type_reference_restrictions())

        symbol_in_matcher = NameAndValue('SYMBOL_IN_MATCHER',
                                         is_any_data_type_reference_restrictions())

        symbol_in_transformer_of_program = NameAndValue('SYMBOL_IN_TRANSFORMER_OF_PROGRAM',
                                                        is_value_type_restriction(ValueType.STRING_TRANSFORMER))

        symbol_in_transformer_of_instruction = NameAndValue('SYMBOL_IN_TRANSFORMER_OF_INSTRUCTION',
                                                            is_value_type_restriction(ValueType.STRING_TRANSFORMER))

        program_with_ref_to_symbols = pgm_args.program(
            pgm_args.interpret_py_source_line(
                self.configuration.py_source_for_print(
                    symbol_reference_syntax_for_name(symbol_in_program_source.name))),
            transformation=symbol_in_transformer_of_program.name
        )
        matcher_with_ref_to_symbol = matcher_arguments.equals_matcher(SymbolReferenceArgument(symbol_in_matcher.name))

        arguments = po_ab.from_program(program_with_ref_to_symbols,
                                       matcher_with_ref_to_symbol,
                                       transformation=symbol_in_transformer_of_instruction.name)

        symbol_usages_assertion = asrt.matches_sequence([
            matches_reference(symbol_in_program_source),
            matches_reference(symbol_in_transformer_of_program),
            matches_reference(symbol_in_transformer_of_instruction),
            matches_reference(symbol_in_matcher),
        ])

        source = arguments.as_remaining_source

        # ACT #

        actual = self.configuration.parser().parse(ARBITRARY_FS_LOCATION_INFO, source)
        actual_symbol_usages = actual.symbol_usages()

        # ASSERT #

        symbol_usages_assertion.apply_without_message(self, actual_symbol_usages)


class TestFailingValidationPreSds(TestCaseBase):
    def runTest(self):
        # ARRANGE #

        program_with_ref_to_file_in_home_ds = pgm_args.program(
            pgm_args.interpret_py_source_file(ab.file_ref_rel_opt('non-existing-file', RelOptionType.REL_HOME_CASE))
        )
        arguments = po_ab.from_program(program_with_ref_to_file_in_home_ds,
                                       matcher_arguments.emptiness_matcher())

        # ACT & ASSERT #

        self._check(arguments,
                    ArrangementPostAct(),
                    Expectation(validation_pre_sds=asrt_svh.is_validation_error()))


class TestFailingValidationPostSds(TestCaseBase):
    def runTest(self):
        # ARRANGE #

        program_with_ref_to_file_in_home_ds = pgm_args.program(
            pgm_args.interpret_py_source_file(ab.file_ref_rel_opt('non-existing-file', RelOptionType.REL_ACT))
        )
        arguments = po_ab.from_program(program_with_ref_to_file_in_home_ds,
                                       matcher_arguments.emptiness_matcher())

        # ACT & ASSERT #

        self._check(arguments,
                    ArrangementPostAct(),
                    Expectation(validation_post_sds=asrt_svh.is_validation_error()))
