import unittest
from abc import ABC, abstractmethod
from typing import List, Sequence

from exactly_lib.impls.types.program.sdvs import command_program_sdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator, ConstantDdvValidator
from exactly_lib.type_val_deps.sym_ref.restrictions import ValueTypeRestriction
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.test_resources.validation import validation
from exactly_lib_test.impls.test_resources.validation.validation_of_path import \
    FAILING_VALIDATION_ASSERTION_FOR_PARTITION
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import AssertionResolvingEnvironment, Expectation, \
    ParseExpectation, MultiSourceExpectation, arrangement_wo_tcds, arrangement_w_tcds, ExecutionExpectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc
from exactly_lib_test.impls.types.program.test_resources import command_driver_sdv_cases, program_sdvs
from exactly_lib_test.impls.types.program.test_resources.command_driver_sdv_cases import CommandDriverSdvCase
from exactly_lib_test.impls.types.test_resources import relativity_options
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.list_.test_resources.symbol_context import ListConstantSymbolContext
from exactly_lib_test.type_val_deps.types.program.test_resources import references
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentOfStringAbsStx, \
    ArgumentOfSymbolReferenceAbsStx, ArgumentOfExistingPathAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.symbol_context import ProgramSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import program_assertions as asrt_pgm_val, \
    command_assertions as asrt_command


class TestExecutorBase(ABC):
    def __init__(self, put: unittest.TestCase):
        self.put = put

    @abstractmethod
    def source_to_parse(self, symbol_name: str, arguments: Sequence[ArgumentAbsStx]) -> AbstractSyntax:
        pass

    @abstractmethod
    def integration_checker(self) -> integration_check.IntegrationChecker[Program, None, None]:
        pass


class ArgumentAccumulationTestExecutor(TestExecutorBase, ABC):
    def run_test(self):
        # ARRANGE #
        arguments_cases = [
            NameAndValue(
                '{} arguments'.format(n),
                ['arg{}'.format(i + 1) for i in range(n)],
            )
            for n in [0, 1, 2]
        ]

        for command_driver_case in command_driver_sdv_cases.all_command_driver_types():
            for arguments_of_referenced_command_case in arguments_cases:
                for accumulated_arguments_of_referenced_program_case in arguments_cases:
                    for additional_arguments_case in arguments_cases:
                        with self.put.subTest(
                                driver=command_driver_case.name,
                                args_of_referenced_command=arguments_of_referenced_command_case.name,
                                accumulated_args_of_referenced_program=accumulated_arguments_of_referenced_program_case.name,
                                additional_args=additional_arguments_case.name,
                        ):
                            # ACT & ASSERT #
                            self._check(command_driver_case,
                                        arguments_of_referenced_command_case.value,
                                        accumulated_arguments_of_referenced_program_case.value,
                                        additional_arguments_case.value)

    def _check(self,
               command_driver: CommandDriverSdvCase,
               arguments_of_referenced_command: List[str],
               accumulated_arguments_of_referenced_program: List[str],
               additional_argument: List[str],
               ):
        # ARRANGE #
        all_arguments = (
                arguments_of_referenced_command +
                accumulated_arguments_of_referenced_program +
                additional_argument
        )

        def expected_program(env: AssertionResolvingEnvironment) -> Assertion[Program]:
            return asrt_pgm_val.matches_program(
                asrt_command.matches_command(
                    driver=command_driver.expected_command_driver(env),
                    arguments=asrt.equals(all_arguments)
                ),
                stdin=asrt_pgm_val.is_no_stdin(),
                transformer=asrt_pgm_val.is_no_transformation(),
            )

        referenced_program_symbol = ProgramSymbolContext.of_sdv(
            'REFERENCED_PROGRAM',
            command_program_sdv.ProgramSdvForCommand(
                CommandSdv(
                    command_driver.command_driver,
                    ArgumentsSdv.new_without_validation(
                        list_sdvs.from_str_constants(arguments_of_referenced_command)
                    )
                ),
                AccumulatedComponents.of_arguments(
                    ArgumentsSdv.new_without_validation(
                        list_sdvs.from_str_constants(accumulated_arguments_of_referenced_program)
                    )
                )
            )
        )
        source_to_parse = self.source_to_parse(
            referenced_program_symbol.name,
            [
                ArgumentOfStringAbsStx.of_str(arg)
                for arg in additional_argument
            ],
        )
        # ACT & ASSERT #
        self.integration_checker().check__abs_stx__wo_input(
            self.put,
            source_to_parse,
            command_driver.mk_arrangement(referenced_program_symbol.symbol_table),
            Expectation(
                parse=ParseExpectation(
                    symbol_references=referenced_program_symbol.references_assertion,
                ),
                primitive=expected_program,
            ),
        )


class SymbolReferencesCase:
    def __init__(self,
                 name: str,
                 source: AbstractSyntax,
                 references_expectation: Assertion[Sequence[SymbolReference]],
                 expected_additional_arguments: List[str],
                 ):
        self.name = name
        self.source = source
        self.references_expectation = references_expectation
        self.expected_additional_arguments = expected_additional_arguments


class SymbolReferencesTestExecutor(TestExecutorBase, ABC):
    def run_test(self):
        # ARRANGE #
        arguments_of_referenced_sdv_symbol = ListConstantSymbolContext(
            'ARGUMENT_OF_SDV_SYMBOL',
            ['argument of sdv 1', 'argument of sdv 2'],
        )

        referenced_system_program_name = 'the-referenced-system-program'
        referenced_program_arguments = arguments_of_referenced_sdv_symbol.constant_list
        referenced_system_program_sdv = program_sdvs.system_program(
            string_sdvs.str_constant(referenced_system_program_name),
            ArgumentsSdv.new_without_validation(
                list_sdvs.from_elements([
                    list_sdvs.symbol_element(
                        SymbolReference(arguments_of_referenced_sdv_symbol.name,
                                        ValueTypeRestriction.of_single(ValueType.LIST)
                                        ))
                ])
            )
        )

        program_symbol = ProgramSymbolContext.of_sdv('PROGRAM_SYMBOL', referenced_system_program_sdv)
        string_argument_symbol = StringConstantSymbolContext('STRING_ARGUMENT_SYMBOL', 'string argument')
        list_argument_symbol = ListConstantSymbolContext('LIST_ARGUMENT_SYMBOL', ['list arg value 1',
                                                                                  'list arg value 2'])
        symbols = SymbolContext.symbol_table_of_contexts([program_symbol,
                                                          arguments_of_referenced_sdv_symbol,
                                                          string_argument_symbol,
                                                          list_argument_symbol])

        cases = [
            SymbolReferencesCase(
                'just program reference symbol',
                self.source_to_parse(program_symbol.name, ()),
                references_expectation=
                asrt.matches_sequence([
                    references.is_reference_to_program(program_symbol.name),
                ]),
                expected_additional_arguments=[],
            ),
            SymbolReferencesCase(
                'arguments that are references to string and list symbols',
                self.source_to_parse(
                    program_symbol.name,
                    [ArgumentOfSymbolReferenceAbsStx(string_argument_symbol.name),
                     ArgumentOfSymbolReferenceAbsStx(list_argument_symbol.name)]
                ),
                references_expectation=
                asrt.matches_sequence([
                    references.is_reference_to_program(program_symbol.name),
                    string_argument_symbol.reference_assertion__w_str_rendering,
                    list_argument_symbol.reference_assertion__w_str_rendering,
                ]),
                expected_additional_arguments=([string_argument_symbol.str_value] +
                                               list_argument_symbol.constant_list),
            ),
        ]
        for case in cases:
            def expected_program(env: AssertionResolvingEnvironment) -> Assertion[Program]:
                return asrt_pgm_val.matches_program(
                    command=asrt_command.equals_system_program_command(
                        program=referenced_system_program_name,
                        arguments=referenced_program_arguments + case.expected_additional_arguments,
                    ),
                    stdin=asrt_pgm_val.is_no_stdin(),
                    transformer=asrt_pgm_val.is_no_transformation(),
                )

            expectation = MultiSourceExpectation(
                symbol_references=case.references_expectation,
                primitive=expected_program,
            )

            with self.put.subTest(case=case.name):
                # ACT & ASSERT #
                self.integration_checker().check__abs_stx__layouts__source_variants__wo_input(
                    self.put,
                    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
                    case.source,
                    arrangement_wo_tcds(
                        symbols=symbols,
                    ),
                    expectation,
                )


class ValidationOfAccumulatedArgumentsExecutor(TestExecutorBase, ABC):
    def __init__(self,
                 put: unittest.TestCase,
                 missing_file_relativity: RelOptionType,
                 ):
        super().__init__(put)
        self._missing_file_relativity = missing_file_relativity

    def run_test(self):
        relativity_conf = relativity_options.conf_rel_any(self._missing_file_relativity)

        referenced_program_arguments = ['valid arg 1 of referenced',
                                        'valid arg 2 of referenced']
        referenced_system_program_sdv = program_sdvs.system_program(
            string_sdvs.str_constant('valid-system-program'),
            ArgumentsSdv.new_without_validation(
                list_sdvs.from_str_constants(referenced_program_arguments)
            )
        )

        valid_program_symbol = ProgramSymbolContext.of_sdv(
            'VALID_PROGRAM',
            referenced_system_program_sdv
        )

        invalid_argument_syntax = ArgumentOfExistingPathAbsStx(
            relativity_conf.path_abs_stx_of_name('non-existing-file')
        )
        reference_and_additional_invalid_argument = self.source_to_parse(
            valid_program_symbol.name,
            [invalid_argument_syntax],
        )
        # ACT & ASSERT #
        self.integration_checker().check__abs_stx__layouts__source_variants__wo_input(
            self.put,
            equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
            reference_and_additional_invalid_argument,
            arrangement_w_tcds(
                symbols=valid_program_symbol.symbol_table,
            ),
            MultiSourceExpectation.of_const(
                symbol_references=valid_program_symbol.references_assertion,
                primitive=asrt.anything_goes(),
                execution=ExecutionExpectation(
                    validation=
                    FAILING_VALIDATION_ASSERTION_FOR_PARTITION[relativity_conf.directory_structure_partition],
                )
            ),
        )


class ValidationOfSdvArgumentsExecutor(TestExecutorBase, ABC):
    def run_test(self):
        def resolve_validator_that_fails_pre_sds(symbols: SymbolTable) -> DdvValidator:
            return ConstantDdvValidator.of_pre_sds(
                asrt_text_doc.new_single_string_text_for_test('err msg')
            )

        referenced_system_program_sdv_w_invalid_arguments = program_sdvs.system_program(
            string_sdvs.str_constant('valid-system-program'),
            ArgumentsSdv(
                list_sdvs.from_str_constant('the arg'),
                [resolve_validator_that_fails_pre_sds]
            )
        )

        valid_program_symbol = ProgramSymbolContext.of_sdv(
            'VALID_PROGRAM',
            referenced_system_program_sdv_w_invalid_arguments
        )

        argument_syntax = ArgumentOfStringAbsStx.of_str('valid-arg')

        reference_and_additional_invalid_argument = self.source_to_parse(
            valid_program_symbol.name,
            [argument_syntax],
        )
        # ACT & ASSERT #
        self.integration_checker().check__abs_stx__layouts__source_variants__wo_input(
            self.put,
            equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
            reference_and_additional_invalid_argument,
            arrangement_w_tcds(
                symbols=valid_program_symbol.symbol_table,
            ),
            MultiSourceExpectation.of_const(
                symbol_references=valid_program_symbol.references_assertion,
                primitive=asrt.anything_goes(),
                execution=ExecutionExpectation(
                    validation=
                    validation.ValidationAssertions.pre_sds_fails__w_any_msg(),
                )
            ),
        )
