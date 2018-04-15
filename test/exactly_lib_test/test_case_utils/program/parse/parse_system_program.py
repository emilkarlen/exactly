import unittest
from typing import List, Set, Callable

from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition, RelOptionType, \
    RESOLVING_DEPENDENCY_OF, RelNonHomeOptionType, RelHomeOptionType
from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib.test_case_utils.program.parse import parse_system_program as sut
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.logic.program.program_value import Program
from exactly_lib.util.parse.token import QuoteType, QUOTE_CHAR_FOR_TYPE
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import resolver_assertions as asrt_resolver
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.test_case.test_resources import validation_check
from exactly_lib_test.test_case_file_structure.test_resources import dir_dep_value_assertions as asrt_dir_dep_val, \
    home_and_sds_populators
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.test_resources import sym_ref_cmd_line_args as sym_ref_args
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_case_utils.test_resources import relativity_options
from exactly_lib_test.test_resources.arguments_building import ArgumentElementRenderer
from exactly_lib_test.test_resources.file_structure import FileSystemElement, empty_file, DirContents
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources import line_transformer_assertions as asrt_line_transformer
from exactly_lib_test.type_system.logic.test_resources import program_assertions as asrt_pgm_val
from exactly_lib_test.util.test_resources import command_assertions as asrt_command


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSuccessfulParse),
        unittest.makeSuite(TestValidationAfterSuccessfulParse),
    ])


class TestFailingParse(unittest.TestCase):
    def test(self):
        # ARRANGE #
        cases = [
            NameAndValue('empty source',
                         ab.empty()
                         ),
            NameAndValue('invalid program name - broken syntax due to missing end quote',
                         sym_ref_args.system_program_cmd_line(
                             QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + 'valid_program_name'),
                         ),
            NameAndValue('invalid argument - broken syntax due to missing end quote',
                         sym_ref_args.system_program_cmd_line('valid_program_name',
                                                              [QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + 'argument'])
                         ),
        ]
        parser = sut.program_parser()
        for case in cases:
            source = parse_source_of(case.value)
            with self.subTest(case.name):
                # ASSERT #
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT #
                    parser.parse(source)


class ProgramNameCase:
    def __init__(self,
                 name: str,
                 source_element,
                 expected_resolved_value: str,
                 expected_symbol_references: List[asrt.ValueAssertion[SymbolReference]]):
        self.name = name
        self.source_element = source_element
        self.expected_resolved_value = expected_resolved_value
        self.expected_symbol_references = expected_symbol_references


class ArgumentsCase:
    def __init__(self,
                 name: str,
                 source_elements: List,
                 expected_dir_dependencies: Set[DirectoryStructurePartition],
                 expected_resolved_values: Callable[[HomeAndSds], List[str]],
                 expected_symbol_references: List[asrt.ValueAssertion[SymbolReference]]):
        self.name = name
        self.source_elements = source_elements
        self.expected_dir_dependencies = expected_dir_dependencies
        self.expected_resolved_values = expected_resolved_values
        self.expected_symbol_references = expected_symbol_references


class TestSuccessfulParse(unittest.TestCase):
    parser = sut.program_parser()

    def test(self):
        # ARRANGE #

        program_name_string_symbol = NameAndValue('PROGRAM_NAME_STRING_SYMBOL_NAME',
                                                  'the program name')

        argument_string_symbol = NameAndValue('ARGUMENT_STRING_SYMBOL_NAME',
                                              'the argument')

        symbols = SymbolTable({
            program_name_string_symbol.name:
                data_symbol_utils.string_constant_container(program_name_string_symbol.value),

            argument_string_symbol.name:
                data_symbol_utils.string_constant_container(argument_string_symbol.value),
        })

        file_name = 'a-file.txt'
        default_relativity_of_existing_file = RelOptionType.REL_HOME_CASE
        file_ref = file_refs.of_rel_option(default_relativity_of_existing_file,
                                           file_refs.constant_path_part(file_name))

        argument_cases = [
            ArgumentsCase('no arguments',
                          source_elements=[],
                          expected_dir_dependencies=set(),
                          expected_resolved_values=lambda tcds: [],
                          expected_symbol_references=[]
                          ),
            ArgumentsCase('single constant argument',
                          source_elements=['argument'],
                          expected_dir_dependencies=set(),
                          expected_resolved_values=lambda tcds: ['argument'],
                          expected_symbol_references=[]
                          ),
            ArgumentsCase('symbol reference and constant argument',
                          source_elements=[ab.symbol_reference(argument_string_symbol.name), 'argument'],
                          expected_dir_dependencies=set(),
                          expected_resolved_values=lambda tcds: [argument_string_symbol.value, 'argument'],
                          expected_symbol_references=[
                              asrt_sym_ref.is_reference_to_data_type_symbol(argument_string_symbol.name)
                          ]
                          ),
            ArgumentsCase('existing file argument',
                          source_elements=[ab.option(syntax_elements.EXISTING_FILE_OPTION_NAME), file_name],
                          expected_dir_dependencies={RESOLVING_DEPENDENCY_OF[default_relativity_of_existing_file]},
                          expected_resolved_values=lambda tcds: [str(file_ref.value_of_any_dependency(tcds))],
                          expected_symbol_references=[]
                          ),
        ]

        program_cases = [
            ProgramNameCase('string constant',
                            source_element='the_program',
                            expected_resolved_value='the_program',
                            expected_symbol_references=[]
                            ),
            ProgramNameCase('symbol reference',
                            source_element=ab.symbol_reference(program_name_string_symbol.name),
                            expected_resolved_value=program_name_string_symbol.value,
                            expected_symbol_references=[
                                asrt_sym_ref.is_reference_to_string_made_up_of_just_plain_strings(
                                    program_name_string_symbol.name)
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
            expected_references_assertion = asrt.matches_sequence(program_case.expected_symbol_references +
                                                                  argument_case.expected_symbol_references)

            def expected_program(tcds: HomeAndSds) -> asrt.ValueAssertion[Program]:
                return asrt_pgm_val.matches_program(
                    command=asrt_command.equals_system_program_command(
                        program=program_case.expected_resolved_value,
                        arguments=argument_case.expected_resolved_values(tcds)
                    ),
                    stdin=asrt_pgm_val.no_stdin(),
                    transformer=asrt_line_transformer.is_identity_transformer()
                )

            expectation = asrt_resolver.matches_resolver_of_program(
                references=expected_references_assertion,
                resolved_program_value=asrt_dir_dep_val.matches_dir_dependent_value(
                    resolving_dependencies=asrt.equals(argument_case.expected_dir_dependencies),
                    resolved_value=expected_program,
                ),
                symbols=symbols
            )

            source = parse_source_of(sym_ref_args.system_program_cmd_line(program_case.source_element,
                                                                          argument_case.source_elements))

            # ACT #

            actual = self.parser.parse(source)

            # ASSERT #

            expectation.apply_without_message(self, actual)


class FileExistenceCase:
    def __init__(self, name: str):
        self.name = name

    def expectation_for(self, step: DirectoryStructurePartition) -> validation_check.Expectation:
        raise NotImplementedError('abstract method')

    def files_for_name(self, file_name: str) -> List[FileSystemElement]:
        raise NotImplementedError('abstract method')


class FileDoExistCase(FileExistenceCase):
    def __init__(self):
        super().__init__('file do exist')

    def expectation_for(self, step: DirectoryStructurePartition) -> validation_check.Expectation:
        return validation_check.is_success()

    def files_for_name(self, file_name: str) -> List[FileSystemElement]:
        return [empty_file(file_name)]


class FileDoNotExistCase(FileExistenceCase):
    def __init__(self):
        super().__init__('file do NOT exist')

    def expectation_for(self, step: DirectoryStructurePartition) -> validation_check.Expectation:
        return validation_check.fails_on(step)

    def files_for_name(self, file_name: str) -> List[FileSystemElement]:
        return []


FILE_EXISTENCE_CASES = [
    FileDoExistCase(),
    FileDoNotExistCase(),
]


class TestValidationAfterSuccessfulParse(unittest.TestCase):
    def test_with_reference_to_existing_file(self):
        referenced_file = 'referenced-file.txt'

        relativity_cases = [
            relativity_options.conf_rel_home(RelHomeOptionType.REL_HOME_CASE),
            relativity_options.conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
        ]
        for file_existence_case in FILE_EXISTENCE_CASES:
            for relativity_conf in relativity_cases:
                arguments = ab.sequence(['program_name',
                                         ab.option(syntax_elements.EXISTING_FILE_OPTION_NAME),
                                         relativity_conf.option_argument,
                                         referenced_file]).as_str

                source = remaining_source(arguments)

                arrangement = validation_check.Arrangement(
                    dir_contents=relativity_conf.populator_for_relativity_option_root(
                        DirContents(file_existence_case.files_for_name(referenced_file))
                    ))
                expectation = file_existence_case.expectation_for(relativity_conf.directory_structure_partition)

                with self.subTest(relativity=relativity_conf.option_string,
                                  file_do_existence_case=file_existence_case.name):
                    program_resolver = sut.program_parser().parse(source)
                    validation_check.check(
                        self,
                        program_resolver.validator,
                        arrangement,
                        expectation,
                    )

    def test_without_reference_to_existing_file(self):
        # ARRANGE #
        arguments = ab.sequence(['program_name',
                                 'argument-that-is-not-a-file']).as_str

        source = remaining_source(arguments)

        arrangement = validation_check.Arrangement(
            dir_contents=home_and_sds_populators.empty()
        )

        expectation = validation_check.is_success()

        # ACT #

        program_resolver = sut.program_parser().parse(source)

        # ASSERT #

        validation_check.check(
            self,
            program_resolver.validator,
            arrangement,
            expectation,
        )


def parse_source_of(single_line: ArgumentElementRenderer) -> ParseSource:
    return ArgumentElements([single_line]).as_remaining_source


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
