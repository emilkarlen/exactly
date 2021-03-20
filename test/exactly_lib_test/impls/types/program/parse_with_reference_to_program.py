import unittest
from typing import Sequence

from exactly_lib.impls.types.program.parse import parse_with_reference_to_program as sut
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.path.path_ddvs import simple_of_rel_option
from exactly_lib.type_val_deps.types.path.path_sdvs import constant
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import MultiSourceExpectation, \
    arrangement_w_tcds, ExecutionExpectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc
from exactly_lib_test.impls.types.program.test_resources import integration_check_config
from exactly_lib_test.impls.types.program.test_resources import invalid_syntax
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.program.test_resources.arguments_accumulation import ArgumentAccumulationTestExecutor, \
    TestExecutorBase, SymbolReferencesTestExecutor, ValidationOfAccumulatedArgumentsExecutor, \
    ValidationOfSdvArgumentsExecutor
from exactly_lib_test.impls.types.test_resources import relativity_options
from exactly_lib_test.section_document.element_parsers.test_resources.parsing import ParserAsLocationAwareParser
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.symbol.test_resources.symbol_syntax import A_VALID_SYMBOL_NAME
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.dep_variants.full_deps.test_resources import common_properties_checker
from exactly_lib_test.type_val_deps.test_resources.validation.validation_of_path import \
    FAILING_VALIDATION_ASSERTION_FOR_PARTITION
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes__raw import \
    RawProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.symbol_context import ProgramSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        TestResolvingAndAccumulation(),
        TestResolvingAndSymbolReferences(),
        unittest.makeSuite(TestValidation),
    ])


class TestFailingParse(unittest.TestCase):
    def test_invalid_plain_symbol_name(self):
        # ARRANGE #
        checker = parse_checker.Checker(ParserAsLocationAwareParser(sut.program_parser()))
        for case in invalid_syntax.plain_symbol_cases():
            with self.subTest(case.name):
                syntax = RawProgramOfSymbolReferenceAbsStx(case.value)
                checker.check_invalid_syntax__abs_stx(self, syntax)

    def test_invalid_arguments(self):
        # ARRANGE #
        checker = parse_checker.Checker(ParserAsLocationAwareParser(sut.program_parser()))
        for case in invalid_syntax.arguments_cases():
            with self.subTest(case.name):
                syntax = RawProgramOfSymbolReferenceAbsStx(A_VALID_SYMBOL_NAME, case.value)
                checker.check_invalid_syntax__abs_stx(self, syntax)


class TestResolvingAndAccumulation(unittest.TestCase):
    def runTest(self):
        executor = _ArgumentAccumulationTestExecutorImpl(self)
        executor.run_test()


class TestResolvingAndSymbolReferences(unittest.TestCase):
    def runTest(self):
        executor = _SymbolReferencesTestExecutorImpl(self)
        executor.run_test()


class TestValidation(unittest.TestCase):
    def test_failing_validation_of_referenced_program__pre_sds(self):
        self._check_failing_validation_of_referenced_program__for_relativity(RelOptionType.REL_HDS_ACT)

    def test_failing_validation_of_referenced_program__post_sds(self):
        self._check_failing_validation_of_referenced_program__for_relativity(RelOptionType.REL_TMP)

    def test_failing_validation_of_accumulated_argument__pre_sds(self):
        executor = _ValidationOfAccumulatedArgumentsExecutorImpl(self, RelOptionType.REL_HDS_CASE)
        executor.run_test()

    def test_failing_validation_of_accumulated_argument__post_sds(self):
        executor = _ValidationOfAccumulatedArgumentsExecutorImpl(self, RelOptionType.REL_ACT)
        executor.run_test()

    def test_failing_validation_of_argument_of_sdv(self):
        executor = _ValidationOfSdvArgumentsExecutorImpl(self)
        executor.run_test()

    def _check_failing_validation_of_referenced_program__for_relativity(self, missing_file_relativity: RelOptionType):
        relativity_conf = relativity_options.conf_rel_any(missing_file_relativity)

        program_symbol_with_ref_to_non_exiting_exe_file = ProgramSymbolContext.of_sdv(
            'PGM_WITH_REF_TO_EXE_FILE',
            program_sdvs.ref_to_exe_file(
                constant(simple_of_rel_option(relativity_conf.relativity_option,
                                              'non-existing-exe-file')))
        )

        program_symbol_with_ref_to_non_exiting_file_as_argument = ProgramSymbolContext.of_sdv(
            'PGM_WITH_ARG_WITH_REF_TO_FILE',
            program_sdvs.interpret_py_source_file_that_must_exist(
                constant(simple_of_rel_option(relativity_conf.relativity_option,
                                              'non-existing-python-file.py')))
        )

        expectation = MultiSourceExpectation.of_const(
            symbol_references=asrt.anything_goes(),
            primitive=asrt.anything_goes(),
            execution=ExecutionExpectation(
                validation=FAILING_VALIDATION_ASSERTION_FOR_PARTITION[relativity_conf.directory_structure_partition],
            )
        )

        symbols = SymbolContext.symbol_table_of_contexts([
            program_symbol_with_ref_to_non_exiting_exe_file,
            program_symbol_with_ref_to_non_exiting_file_as_argument,
        ])
        arrangement = arrangement_w_tcds(
            symbols=symbols,
        )

        cases = [
            NameAndValue(
                'executable does not exist',
                RawProgramOfSymbolReferenceAbsStx(program_symbol_with_ref_to_non_exiting_exe_file.name),
            ),
            NameAndValue(
                'file referenced from argument does not exist',
                RawProgramOfSymbolReferenceAbsStx(program_symbol_with_ref_to_non_exiting_file_as_argument.name),
            ),
        ]

        for case in cases:
            with self.subTest(case=case.name):
                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
                    case.value,
                    arrangement,
                    expectation,
                )


class _TestExecutorImplBase(TestExecutorBase):
    def source_to_parse(self, symbol_name: str, arguments: Sequence[ArgumentAbsStx]) -> AbstractSyntax:
        return RawProgramOfSymbolReferenceAbsStx(symbol_name, arguments)

    def integration_checker(self) -> integration_check.IntegrationChecker[Program, None, None]:
        return CHECKER_WO_EXECUTION


class _ArgumentAccumulationTestExecutorImpl(ArgumentAccumulationTestExecutor, _TestExecutorImplBase):
    pass


class _SymbolReferencesTestExecutorImpl(SymbolReferencesTestExecutor, _TestExecutorImplBase):
    pass


class _ValidationOfAccumulatedArgumentsExecutorImpl(ValidationOfAccumulatedArgumentsExecutor, _TestExecutorImplBase):
    pass


class _ValidationOfSdvArgumentsExecutorImpl(ValidationOfSdvArgumentsExecutor, _TestExecutorImplBase):
    pass


CHECKER_WO_EXECUTION = integration_check.IntegrationChecker(
    sut.program_parser(),
    integration_check_config.ProgramPropertiesConfiguration(
        common_properties_checker.ApplierThatDoesNothing(),
    ),
    True,
)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
