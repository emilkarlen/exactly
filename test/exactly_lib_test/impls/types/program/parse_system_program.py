import unittest
from typing import List, Callable, TypeVar, Sequence

from exactly_lib.impls.types.program.parse import parse_system_program as sut
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition, RelOptionType, \
    RelNonHdsOptionType, RelHdsOptionType
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType, QUOTE_CHAR_FOR_TYPE
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import MultiSourceExpectation, \
    AssertionResolvingEnvironment, arrangement_w_tcds, ExecutionExpectation, arrangement_wo_tcds
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc
from exactly_lib_test.impls.types.program.test_resources import integration_check_config
from exactly_lib_test.impls.types.test_resources import relativity_options
from exactly_lib_test.section_document.element_parsers.test_resources.parsing import ParserAsLocationAwareParser
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import tcds_populators
from exactly_lib_test.test_resources.files.file_structure import FileSystemElement, DirContents, File
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.full_deps.test_resources import common_properties_checker
from exactly_lib_test.type_val_deps.test_resources.validation import validation
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.type_val_deps.test_resources.validation.validation_of_path import \
    FAILING_VALIDATION_ASSERTION_FOR_PARTITION
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes__raw import \
    RawSystemCommandLineAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import \
    ArgumentOfSymbolReferenceAbsStx, ArgumentOfExistingPathAbsStx, NonSymLinkFileType, ArgumentOfRichStringAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.abstract_syntaxes import StringSymbolAbsStx
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command, \
    program_assertions as asrt_pgm_val


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFailingParse(),
        TestSuccessfulParse(),
        unittest.makeSuite(TestValidation),
    ])


class TestFailingParse(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NameAndValue('empty source',
                         RawSystemCommandLineAbsStx.of_str(''),
                         ),
            NameAndValue('invalid program name - broken syntax due to missing end quote',
                         RawSystemCommandLineAbsStx.of_str(
                             QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + 'valid_program_name'),
                         ),
            NameAndValue('invalid argument - broken syntax due to missing end quote',
                         RawSystemCommandLineAbsStx.of_str(
                             'valid_program_name',
                             [ArgumentOfRichStringAbsStx.of_str(QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + 'argument')])
                         ),
        ]
        checker = parse_checker.Checker(ParserAsLocationAwareParser(sut.program_parser()))
        for case in cases:
            checker.check_invalid_syntax__abs_stx(self, case.value)


T = TypeVar('T')


class ProgramNameCase:
    def __init__(self,
                 name: str,
                 source_element: RawSystemCommandLineAbsStx,
                 expected_resolved_value: str,
                 expected_symbol_references: List[Assertion[SymbolReference]]):
        self.name = name
        self.source_element = source_element
        self.expected_resolved_value = expected_resolved_value
        self.expected_symbol_references = expected_symbol_references


class ArgumentsCase:
    def __init__(self,
                 name: str,
                 source_elements: Sequence[ArgumentAbsStx],
                 expected_resolved_values: Callable[[TestCaseDs], List[str]],
                 expected_symbol_references: List[Assertion[SymbolReference]],
                 tcds_contents: tcds_populators.TcdsPopulator = tcds_populators.empty(),
                 ):
        self.name = name
        self.source_elements = source_elements
        self.expected_resolved_values = expected_resolved_values
        self.expected_symbol_references = expected_symbol_references
        self.tcds_contents = tcds_contents


class TestSuccessfulParse(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        program_name_string_symbol = StringConstantSymbolContext('PROGRAM_NAME_STRING_SYMBOL_NAME',
                                                                 'the program name')

        argument_string_symbol = StringConstantSymbolContext('ARGUMENT_STRING_SYMBOL_NAME',
                                                             'the argument')

        symbols = SymbolContext.symbol_table_of_contexts([
            program_name_string_symbol,
            argument_string_symbol,
        ])

        file_name = 'a-file.txt'
        file_arg_relativity = relativity_options.conf_rel_any(RelOptionType.REL_HDS_CASE)
        path = path_ddvs.of_rel_option(file_arg_relativity.relativity_option,
                                       path_ddvs.constant_path_part(file_name))

        argument_cases = [
            ArgumentsCase('no arguments',
                          source_elements=[],
                          expected_resolved_values=lambda tcds: [],
                          expected_symbol_references=[],
                          ),
            ArgumentsCase('single constant argument',
                          source_elements=[ArgumentOfRichStringAbsStx.of_str('argument')],
                          expected_resolved_values=lambda tcds: ['argument'],
                          expected_symbol_references=[],
                          ),
            ArgumentsCase('symbol reference and constant argument',
                          source_elements=[ArgumentOfSymbolReferenceAbsStx(argument_string_symbol.name),
                                           ArgumentOfRichStringAbsStx.of_str('argument')],
                          expected_resolved_values=lambda tcds: [argument_string_symbol.str_value, 'argument'],
                          expected_symbol_references=[
                              argument_string_symbol.reference_assertion__w_str_rendering
                          ]),
            ArgumentsCase('existing file argument',
                          source_elements=[
                              ArgumentOfExistingPathAbsStx(file_arg_relativity.path_abs_stx_of_name(file_name),
                                                           NonSymLinkFileType.REGULAR)],
                          expected_resolved_values=lambda tcds: [str(path.value_of_any_dependency(tcds))],
                          expected_symbol_references=[],
                          tcds_contents=file_arg_relativity.populator_for_relativity_option_root(
                              DirContents([File.empty(file_name)])
                          )
                          ),
        ]

        program_cases = [
            ProgramNameCase('string constant',
                            source_element=RawSystemCommandLineAbsStx.of_str('the_program'),
                            expected_resolved_value='the_program',
                            expected_symbol_references=[]
                            ),
            ProgramNameCase('symbol reference',
                            source_element=RawSystemCommandLineAbsStx(
                                StringSymbolAbsStx(program_name_string_symbol.name)
                            ),
                            expected_resolved_value=program_name_string_symbol.str_value,
                            expected_symbol_references=[
                                program_name_string_symbol.reference_assertion__string__w_all_indirect_refs_are_strings
                            ]
                            ),
        ]

        for argument_case in argument_cases:
            for program_case in program_cases:
                # ACT & ASSERT #
                self._check(program_case, argument_case, symbols)

    def _check(self,
               program_case: ProgramNameCase,
               argument_case: ArgumentsCase,
               symbols: SymbolTable):
        with self.subTest(program=program_case.name,
                          arguments=argument_case.name):
            _check_parsing_of_program(self,
                                      program_case,
                                      argument_case,
                                      symbols)


class FileExistenceCase:
    def __init__(self, name: str):
        self.name = name

    def expectation_for(self, step: DirectoryStructurePartition) -> ValidationAssertions:
        raise NotImplementedError('abstract method')

    def files_for_name(self, file_name: str) -> List[FileSystemElement]:
        raise NotImplementedError('abstract method')


class FileDoExistCase(FileExistenceCase):
    def __init__(self):
        super().__init__('file do exist')

    def expectation_for(self, step: DirectoryStructurePartition) -> ValidationAssertions:
        return validation.ValidationAssertions.all_passes()

    def files_for_name(self, file_name: str) -> List[FileSystemElement]:
        return [File.empty(file_name)]


class FileDoNotExistCase(FileExistenceCase):
    def __init__(self):
        super().__init__('file do NOT exist')

    def expectation_for(self, step: DirectoryStructurePartition) -> ValidationAssertions:
        return FAILING_VALIDATION_ASSERTION_FOR_PARTITION[step]

    def files_for_name(self, file_name: str) -> List[FileSystemElement]:
        return []


FILE_EXISTENCE_CASES = [
    FileDoExistCase(),
    FileDoNotExistCase(),
]


class TestValidation(unittest.TestCase):
    def test_with_reference_to_existing_file(self):
        referenced_file = 'referenced-file.txt'

        relativity_cases = [
            relativity_options.conf_rel_hds(RelHdsOptionType.REL_HDS_CASE),
            relativity_options.conf_rel_non_hds(RelNonHdsOptionType.REL_ACT),
        ]
        for file_existence_case in FILE_EXISTENCE_CASES:
            for relativity_conf in relativity_cases:
                source_syntax = RawSystemCommandLineAbsStx.of_str(
                    'program_name',
                    [ArgumentOfExistingPathAbsStx(relativity_conf.path_abs_stx_of_name(referenced_file))]
                )

                with self.subTest(relativity=relativity_conf.option_string,
                                  file_do_existence_case=file_existence_case.name):
                    # ACT & ASSERT #
                    CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
                        self,
                        equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
                        source_syntax,
                        arrangement_w_tcds(
                            tcds_contents=relativity_conf.populator_for_relativity_option_root(
                                DirContents(file_existence_case.files_for_name(referenced_file))
                            )
                        ),
                        MultiSourceExpectation(
                            execution=ExecutionExpectation(
                                validation=file_existence_case.expectation_for(
                                    relativity_conf.directory_structure_partition
                                )
                            )
                        ),
                    )

    def test_without_reference_to_existing_file(self):
        # ARRANGE #
        abstract_syntax = RawSystemCommandLineAbsStx.of_str(
            'program_name',
            [ArgumentOfRichStringAbsStx.of_str('argument-that-is-not-a-file')]
        )
        # ACT & ASSERT #
        CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
            self,
            equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
            abstract_syntax,
            arrangement_wo_tcds(),
            MultiSourceExpectation(
                execution=ExecutionExpectation(
                    validation=validation.ValidationAssertions.all_passes()
                )
            ),
        )


def _check_parsing_of_program(put: unittest.TestCase,
                              program_case: ProgramNameCase,
                              argument_case: ArgumentsCase,
                              symbols: SymbolTable):
    # ARRANGE #
    with put.subTest(program=program_case.name,
                     arguments=argument_case.name):
        expected_references_assertion = asrt.matches_sequence(program_case.expected_symbol_references +
                                                              argument_case.expected_symbol_references)

        def expected_program(env: AssertionResolvingEnvironment) -> Assertion[Program]:
            return asrt_pgm_val.matches_program(
                command=asrt_command.equals_system_program_command(
                    program=program_case.expected_resolved_value,
                    arguments=argument_case.expected_resolved_values(env.tcds)
                ),
                stdin=asrt_pgm_val.is_no_stdin(),
                transformer=asrt_pgm_val.is_no_transformation(),
            )

        expectation = MultiSourceExpectation(
            symbol_references=expected_references_assertion,
            primitive=expected_program,
        )
        source_abs_stx = program_case.source_element.new_w_additional_arguments(argument_case.source_elements)

        # ACT & ASSERT #
        CHECKER_WO_EXECUTION.check__abs_stx__layouts__source_variants__wo_input(
            put,
            equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
            source_abs_stx,
            arrangement_w_tcds(
                symbols=symbols,
                tcds_contents=argument_case.tcds_contents,
            ),
            expectation,
        )


CHECKER_WO_EXECUTION = integration_check.IntegrationChecker(
    sut.program_parser(),
    integration_check_config.ProgramPropertiesConfiguration(
        common_properties_checker.ApplierThatDoesNothing(),
    ),
    True,
)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
