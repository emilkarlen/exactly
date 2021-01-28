import unittest
from typing import Sequence, List

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType
from exactly_lib_test.impls.test_resources.validation.validation_of_path import \
    FAILING_VALIDATION_ASSERTION_FOR_PARTITION
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import MultiSourceExpectation, arrangement_w_tcds, \
    ExecutionExpectation, AssertionResolvingEnvironment, arrangement_wo_tcds
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.parse_program.test_resources.integration_checker import CHECKER_WO_EXECUTION
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.program.test_resources.arguments_accumulation import ArgumentAccumulationTestExecutor, \
    TestExecutorBase, SymbolReferencesTestExecutor, ValidationOfAccumulatedArgumentsExecutor, \
    ValidationOfSdvArgumentsExecutor
from exactly_lib_test.impls.types.test_resources import relativity_options
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.data.test_resources.concrete_restriction_assertion import \
    is_reference_restrictions__to_type_convertible_to_string
from exactly_lib_test.type_val_deps.types.list_.test_resources.list_ import ListConstantSymbolContext
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import PgmAndArgsWArgumentsAbsStx, \
    ProgramOfShellCommandLineAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentOfStringAbsStx, \
    ArgumentOfSymbolReferenceAbsStx, ArgumentOfExistingPathAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.abstract_syntaxes import StringLiteralAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command, \
    program_assertions as asrt_pgm_val


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDriverTypesWArgListExceptSymbolReference),
        unittest.makeSuite(TestShellArgumentsAndSymbolReferences),
        TestAccumulationOfSymbolReferenceArguments(),
        TestSymbolReferencesOfSymRefProgram(),
        unittest.makeSuite(TestValidationOfAccumulatedArguments),
    ])


class ArgumentsCase:
    def __init__(self,
                 name: str,
                 arguments: Sequence[ArgumentAbsStx],
                 expected_arguments: List[str],
                 symbols: Sequence[SymbolContext],
                 ):
        self.name = name
        self.arguments = arguments
        self.expected_arguments = expected_arguments
        self.symbols = symbols


class TestDriverTypesWArgListExceptSymbolReference(unittest.TestCase):
    def test_list_of_arguments_and_symbol_references(self):
        arg_wo_space = 'arg_wo_space'
        arg_w_space = 'an arg w space'
        string_symbol_1 = StringConstantSymbolContext(
            'STRING_SYMBOL_1',
            'value of string symbol 1',
            default_restrictions=is_reference_restrictions__to_type_convertible_to_string(),
        )
        string_symbol_2 = StringConstantSymbolContext(
            'STRING_SYMBOL_2',
            'value of string symbol 2',
            default_restrictions=is_reference_restrictions__to_type_convertible_to_string(),
        )
        arguments_cases = [
            ArgumentsCase(
                'one / wo symbol references',
                arguments=[ArgumentOfStringAbsStx.of_str(arg_w_space, QuoteType.SOFT)],
                expected_arguments=[arg_w_space],
                symbols=(),
            ),
            ArgumentsCase(
                'two / wo symbol references',
                arguments=[ArgumentOfStringAbsStx.of_str(arg_wo_space),
                           ArgumentOfStringAbsStx.of_str(arg_w_space, QuoteType.HARD)],
                expected_arguments=[arg_wo_space, arg_w_space],
                symbols=(),
            ),
            ArgumentsCase(
                'three / w symbol references',
                arguments=[ArgumentOfSymbolReferenceAbsStx(string_symbol_1.name),
                           ArgumentOfStringAbsStx.of_str(arg_w_space, QuoteType.HARD),
                           ArgumentOfSymbolReferenceAbsStx(string_symbol_2.name)],
                expected_arguments=[string_symbol_1.str_value, arg_w_space, string_symbol_2.str_value],
                symbols=[string_symbol_1, string_symbol_2],
            ),
        ]
        # ARRANGE #
        for pgm_and_args_case in pgm_and_args_cases.cases__w_argument_list__excluding_program_reference():
            for arguments_case in arguments_cases:
                pgm_w_args = PgmAndArgsWArgumentsAbsStx(pgm_and_args_case.pgm_and_args,
                                                        arguments_case.arguments)
                expected_arguments = asrt.equals(arguments_case.expected_arguments)
                symbols = list(pgm_and_args_case.symbols) + list(arguments_case.symbols)
                expectation = MultiSourceExpectation(
                    symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                    primitive=lambda env: (
                        asrt_pgm_val.matches_program(
                            asrt_command.matches_command(
                                driver=pgm_and_args_case.expected_command_driver(env),
                                arguments=expected_arguments,
                            ),
                            stdin=asrt_pgm_val.is_no_stdin(),
                            transformer=asrt_pgm_val.is_no_transformation(),
                        ))
                )
                with self.subTest(command=pgm_and_args_case.name,
                                  arguments=arguments_case.name):
                    # ACT & ASSERT #
                    CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                        self,
                        equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
                        pgm_w_args,
                        pgm_and_args_case.mk_arrangement(
                            SymbolContext.symbol_table_of_contexts(symbols)),
                        expectation,
                    )

    def test_validation_pre_sds(self):
        self._check_failing_validation___for_relativity(RelOptionType.REL_HDS_CASE)

    def test_validation_post_sds(self):
        self._check_failing_validation___for_relativity(RelOptionType.REL_ACT)

    def _check_failing_validation___for_relativity(self, missing_file_relativity: RelOptionType):
        relativity_conf = relativity_options.conf_rel_any(missing_file_relativity)

        invalid_argument_syntax = ArgumentOfExistingPathAbsStx(
            relativity_conf.path_abs_stx_of_name('non-existing-file')
        )

        arguments_cases = [
            NameAndValue(
                '1st argument fails validation',
                [invalid_argument_syntax],
            ),
            NameAndValue(
                '2nd argument fails validation',
                [ArgumentOfStringAbsStx.of_str('valid1'),
                 invalid_argument_syntax,
                 ArgumentOfStringAbsStx.of_str('valid2')],
            ),
        ]

        for pgm_and_args_case in pgm_and_args_cases.cases__w_argument_list__excluding_program_reference():
            for arguments_case in arguments_cases:
                pgm_w_args = PgmAndArgsWArgumentsAbsStx(pgm_and_args_case.pgm_and_args,
                                                        arguments_case.value)
                with self.subTest(pgm_and_args=pgm_and_args_case.name,
                                  arguments=arguments_case.name):
                    # ACT & ASSERT #
                    CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                        self,
                        equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
                        pgm_w_args,
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(pgm_and_args_case.symbols),
                            tcds_contents=pgm_and_args_case.tcds,
                        ),
                        MultiSourceExpectation.of_const(
                            symbol_references=SymbolContext.references_assertion_of_contexts(pgm_and_args_case.symbols),
                            primitive=asrt.anything_goes(),
                            execution=ExecutionExpectation(
                                validation=
                                FAILING_VALIDATION_ASSERTION_FOR_PARTITION[
                                    relativity_conf.directory_structure_partition],
                            )
                        ),
                    )


class TestValidationOfAccumulatedArguments(unittest.TestCase):
    def test_failing_validation_of_accumulated_argument__pre_sds(self):
        executor = _ValidationOfAccumulatedArgumentsExecutorImpl(self, RelOptionType.REL_HDS_CASE)
        executor.run_test()

    def test_failing_validation_of_accumulated_argument__post_sds(self):
        executor = _ValidationOfAccumulatedArgumentsExecutorImpl(self, RelOptionType.REL_ACT)
        executor.run_test()

    def test_failing_validation_of_argument_of_sdv(self):
        executor = _ValidationOfSdvArgumentsExecutorImpl(self)
        executor.run_test()


class TestAccumulationOfSymbolReferenceArguments(unittest.TestCase):
    def runTest(self):
        executor = _ArgumentAccumulationTestExecutorImpl(self)
        executor.run_test()


class TestSymbolReferencesOfSymRefProgram(unittest.TestCase):
    def runTest(self):
        executor = _SymbolReferencesOfSymRefProgramTestExecutorImpl(self)
        executor.run_test()


class TestShellArgumentsAndSymbolReferences(unittest.TestCase):
    def test_shell_program(self):
        argument_string_template = 'first {string_symbol} between {list_symbol} after'
        string_argument_symbol = StringConstantSymbolContext(
            'STRING_ARGUMENT_SYMBOL',
            'string argument',
        )
        list_argument_symbol = ListConstantSymbolContext('LIST_ARGUMENT_SYMBOL',
                                                         ['list_arg_value_1',
                                                          'list arg value 2'])
        symbols = [string_argument_symbol, list_argument_symbol]

        command_line_syntax_str = argument_string_template.format(
            string_symbol=string_argument_symbol.name__sym_ref_syntax,
            list_symbol=list_argument_symbol.name__sym_ref_syntax,
        )

        command_line_str = argument_string_template.format(
            string_symbol=string_argument_symbol.str_value,
            list_symbol=' '.join(list_argument_symbol.constant_list),
        )

        syntax = ProgramOfShellCommandLineAbsStx(
            StringLiteralAbsStx(command_line_syntax_str)
        )

        def expected_program(env: AssertionResolvingEnvironment) -> ValueAssertion[Program]:
            return asrt_pgm_val.matches_program(
                command=asrt_command.equals_shell_command(
                    command_line=command_line_str,
                    arguments=[],
                ),
                stdin=asrt_pgm_val.is_no_stdin(),
                transformer=asrt_pgm_val.is_no_transformation(),
            )

        expectation = MultiSourceExpectation(
            symbol_references=asrt.matches_sequence([
                string_argument_symbol.reference_assertion__convertible_to_string,
                list_argument_symbol.reference_assertion__convertible_to_string,
            ]),
            primitive=expected_program,
        )

        # ACT & ASSERT #
        CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
            self,
            equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
            syntax,
            arrangement_wo_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
            ),
            expectation,
        )

    def test_shell_program_via_symbol_reference(self):
        shell_command_line_of_referenced_program = 'initial shell command line'
        arguments_of_referenced_program = ['arg1', 'arg 2']
        referenced_shell_program_sdv = program_sdvs.shell_program(
            string_sdvs.str_constant(shell_command_line_of_referenced_program),
            ArgumentsSdv.new_without_validation(
                list_sdvs.from_str_constants(arguments_of_referenced_program)
            ),
        )
        referenced_program_symbol = ProgramSymbolContext.of_sdv(
            'SHELL_PROGRAM_REFERENCE',
            referenced_shell_program_sdv,
        )

        string_argument_symbol = StringConstantSymbolContext(
            'STRING_ARGUMENT_SYMBOL',
            'string argument',
        )
        list_argument_symbol = ListConstantSymbolContext('LIST_ARGUMENT_SYMBOL',
                                                         ['list_arg_value_1',
                                                          'list arg value 2'])
        str_w_list_template = 'before{}after'
        str_w_list_ref = str_w_list_template.format(list_argument_symbol.name__sym_ref_syntax)

        expected_argument_strings = (
                arguments_of_referenced_program +
                [string_argument_symbol.str_value] +
                list_argument_symbol.constant_list +
                [str_w_list_template.format(' '.join(list_argument_symbol.constant_list))]
        )

        symbols = [referenced_program_symbol, string_argument_symbol, list_argument_symbol]

        syntax = ProgramOfSymbolReferenceAbsStx(
            referenced_program_symbol.name,
            [
                ArgumentOfSymbolReferenceAbsStx(string_argument_symbol.name),
                ArgumentOfSymbolReferenceAbsStx(list_argument_symbol.name),
                ArgumentOfStringAbsStx.of_str(str_w_list_ref),
            ]
        )

        def expected_program(env: AssertionResolvingEnvironment) -> ValueAssertion[Program]:
            return asrt_pgm_val.matches_program(
                command=asrt_command.equals_shell_command(
                    command_line=shell_command_line_of_referenced_program,
                    arguments=expected_argument_strings,
                ),
                stdin=asrt_pgm_val.is_no_stdin(),
                transformer=asrt_pgm_val.is_no_transformation(),
            )

        expectation = MultiSourceExpectation(
            symbol_references=asrt.matches_sequence([
                referenced_program_symbol.reference_assertion,
                string_argument_symbol.reference_assertion__convertible_to_string,
                list_argument_symbol.reference_assertion__convertible_to_string,
                list_argument_symbol.reference_assertion__convertible_to_string,
            ]),
            primitive=expected_program,
        )

        # ACT & ASSERT #
        CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
            self,
            equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
            syntax,
            arrangement_wo_tcds(
                symbols=SymbolContext.symbol_table_of_contexts(symbols),
            ),
            expectation,
        )


class _TestExecutorImplBase(TestExecutorBase):
    def source_to_parse(self, symbol_name: str, arguments: Sequence[ArgumentAbsStx]) -> AbstractSyntax:
        return ProgramOfSymbolReferenceAbsStx(symbol_name, arguments)

    def integration_checker(self) -> integration_check.IntegrationChecker[Program, None, None]:
        return CHECKER_WO_EXECUTION


class _ArgumentAccumulationTestExecutorImpl(ArgumentAccumulationTestExecutor, _TestExecutorImplBase):
    pass


class _SymbolReferencesOfSymRefProgramTestExecutorImpl(SymbolReferencesTestExecutor, _TestExecutorImplBase):
    pass


class _ValidationOfAccumulatedArgumentsExecutorImpl(ValidationOfAccumulatedArgumentsExecutor, _TestExecutorImplBase):
    pass


class _ValidationOfSdvArgumentsExecutorImpl(ValidationOfSdvArgumentsExecutor, _TestExecutorImplBase):
    pass


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
