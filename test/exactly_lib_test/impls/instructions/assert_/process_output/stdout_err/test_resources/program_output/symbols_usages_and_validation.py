import unittest

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err.test_resources.program_output import \
    configuration, \
    arguments_building as po_ab
from exactly_lib_test.impls.instructions.assert_.process_output.stdout_err.test_resources.program_output.utils import \
    matches_reference
from exactly_lib_test.impls.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.impls.types.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.impls.types.string_matcher.test_resources import matcher_arguments
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources.arguments_building import SymbolReferenceArgument
from exactly_lib_test.tcfs.test_resources import path_arguments
from exactly_lib_test.test_case.result.test_resources import svh_assertions as asrt_svh, pfh_assertions as asrt_pfh
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.any_.restrictions_assertions import \
    is_reference_restrictions__value_type
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions
from exactly_lib_test.type_val_deps.types.string_source.test_resources import references as ss_references


def suite_for(conf: configuration.ProgramOutputInstructionConfiguration) -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSymbolReferences(conf),
        TestFailingValidationPreSds(conf),
        TestFailingValidationPostSds(conf),
    ])


class TestSymbolReferences(configuration.TestCaseBase):
    def runTest(self):
        # ARRANGE #

        symbol_in_program_source = NameAndValue('SYMBOL_IN_PROGRAM_SOURCE',
                                                data_restrictions_assertions.is__w_str_rendering())

        symbol_in_matcher = NameAndValue('SYMBOL_IN_MATCHER',
                                         ss_references.IS_STRING_SOURCE_OR_STRING_REFERENCE_RESTRICTION)

        symbol_in_transformer_of_program = NameAndValue('SYMBOL_IN_TRANSFORMER_OF_PROGRAM',
                                                        is_reference_restrictions__value_type(
                                                            [ValueType.STRING_TRANSFORMER]))

        symbol_in_transformer_of_instruction = NameAndValue('SYMBOL_IN_TRANSFORMER_OF_INSTRUCTION',
                                                            is_reference_restrictions__value_type(
                                                                [ValueType.STRING_TRANSFORMER]))

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


class TestFailingValidationPreSds(configuration.TestCaseBase):
    def runTest(self):
        # ARRANGE #

        program_with_ref_to_file_in_hds_ds = pgm_args.program(
            pgm_args.interpret_py_source_file(path_arguments.RelOptPathArgument('non-existing-file',
                                                                                RelOptionType.REL_HDS_CASE))
        )
        arguments = po_ab.from_program(program_with_ref_to_file_in_hds_ds,
                                       matcher_arguments.emptiness_matcher())

        # ACT & ASSERT #

        self._check(arguments,
                    ArrangementPostAct(),
                    Expectation(validation_pre_sds=asrt_svh.is_validation_error()))


class TestFailingValidationPostSds(configuration.TestCaseBase):
    def runTest(self):
        # ARRANGE #

        program_with_ref_to_file_in_hds_ds = pgm_args.program(
            pgm_args.interpret_py_source_file(path_arguments.RelOptPathArgument('non-existing-file',
                                                                                RelOptionType.REL_ACT))
        )
        arguments = po_ab.from_program(program_with_ref_to_file_in_hds_ds,
                                       matcher_arguments.emptiness_matcher())

        # ACT & ASSERT #

        self._check(arguments,
                    ArrangementPostAct(),
                    Expectation(
                        main_result=asrt_pfh.is_hard_error__with_arbitrary_message())
                    )
