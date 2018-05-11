import unittest
from typing import List, Callable, Dict

from exactly_lib.instructions.multi_phase_instructions import new_file as sut
from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.data import string_resolvers
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.data import file_refs
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase_instructions.new_file.test_resources import \
    arguments_building as instr_args
from exactly_lib_test.instructions.multi_phase_instructions.new_file.test_resources.common_test_cases import \
    InvalidDestinationFileTestCasesData, \
    TestCommonFailingScenariosDueToInvalidDestinationFileBase
from exactly_lib_test.instructions.multi_phase_instructions.new_file.test_resources.common_test_cases import \
    TestCaseBase
from exactly_lib_test.instructions.multi_phase_instructions.new_file.test_resources.utils import \
    IS_FAILURE, IS_SUCCESS, AN_ALLOWED_DST_FILE_RELATIVITY
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.utils.parse.parse_file_maker.test_resources.arguments import \
    TransformableContentsConstructor, output_from_program
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    equals_data_type_reference_restrictions
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.symbol.test_resources import program as asrt_pgm
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.lines_transformer import StringTransformerResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.lines_transformer import is_reference_to_lines_transformer
from exactly_lib_test.symbol.test_resources.symbol_usage_assertions import matches_reference_2
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import RelOptFileRefArgument
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    non_home_dir_contains_exactly, dir_contains_exactly
from exactly_lib_test.test_case_utils.parse.parse_file_ref import file_ref_or_string_reference_restrictions
from exactly_lib_test.test_case_utils.parse.test_resources import arguments_building as arg
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import command_cmd_line_args as sym_ref_args
from exactly_lib_test.test_case_utils.program.test_resources import program_resolvers
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.arguments_building import Stringable
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.programs.shell_commands import command_that_prints_line_to_stdout
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, file_assertions as f_asrt
from exactly_lib_test.type_system.logic.test_resources.string_transformers import \
    MyToUppercaseTransformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenariosWithDifferentSourceVariants),
        unittest.makeSuite(TestSuccessfulScenariosWithProgramFromDifferentChannels),
        unittest.makeSuite(TestFailingScenarios),
        unittest.makeSuite(TestSymbolUsages),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
        unittest.makeSuite(TestFailingValidation),
    ])


class TestSymbolUsages(TestCaseBase):
    def test_symbol_usages(self):
        # ARRANGE #
        text_printed_by_shell_command_symbol = NameAndValue('STRING_TO_PRINT_SYMBOL', 'hello_world')

        dst_file_symbol = NameAndValue('DST_FILE_SYMBOL', 'dst-file-name.txt')

        to_upper_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            StringTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))

        transformed_shell_contents_arguments = TransformableContentsConstructor(
            output_from_program(ProcOutputFile.STDOUT,
                                pgm_args.shell_command(
                                    shell_commands.command_that_prints_line_to_stdout(
                                        symbol_reference_syntax_for_name(text_printed_by_shell_command_symbol.name)
                                    ))
                                )
        ).with_transformation(to_upper_transformer.name).as_arguments

        source = remaining_source(
            '{file_name} {content_arguments}'.format(
                file_name=symbol_reference_syntax_for_name(dst_file_symbol.name),
                content_arguments=transformed_shell_contents_arguments.first_line
            ),
            transformed_shell_contents_arguments.following_lines)

        symbols = SymbolTable({
            dst_file_symbol.name:
                container(file_ref_resolvers.of_rel_option(RelOptionType.REL_ACT,
                                                           file_refs.constant_path_part(dst_file_symbol.value))),

            text_printed_by_shell_command_symbol.name:
                container(string_resolvers.str_constant(text_printed_by_shell_command_symbol.value)),

            to_upper_transformer.name:
                container(to_upper_transformer.value),
        })

        # ACT & ASSERT #

        self._check(source,
                    ArrangementWithSds(
                        symbols=symbols,
                    ),
                    Expectation(
                        main_result=IS_SUCCESS,
                        symbol_usages=asrt.matches_sequence([

                            equals_symbol_reference(
                                SymbolReference(dst_file_symbol.name,
                                                file_ref_or_string_reference_restrictions(
                                                    sut.REL_OPT_ARG_CONF.options.accepted_relativity_variants))
                            ),

                            matches_reference_2(
                                text_printed_by_shell_command_symbol.name,
                                equals_data_type_reference_restrictions(is_any_data_type())),

                            is_reference_to_lines_transformer(to_upper_transformer.name),
                        ]),
                    )
                    )


class ProgramCase:
    def __init__(self,
                 name: str,
                 source: ArgumentElements,
                 expected_reference: List[asrt.ValueAssertion[SymbolReference]]):
        self.name = name
        self.source = source
        self.expected_references = expected_reference


class TestSuccessfulScenariosWithProgramFromDifferentChannels(TestCaseBase):
    def test_with_transformation(self):
        text_printed_by_program = 'the text printed by the program'
        transformer = NameAndValue('TO_UPPER_CASE',
                                   StringTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        self._test(
            text_printed_by_program=text_printed_by_program,
            expected_file_contents=text_printed_by_program.upper(),
            make_arguments=lambda tcc: tcc.with_transformation(transformer.name),
            additional_symbols={transformer.name: symbol_utils.container(transformer.value)},
            additional_symbol_references=[is_reference_to_lines_transformer(transformer.name)]
        )

    def test_without_transformation(self):
        text_printed_by_program = 'the text printed by the program'
        self._test(
            text_printed_by_program=text_printed_by_program,
            expected_file_contents=text_printed_by_program,
            make_arguments=lambda tcc: tcc.without_transformation(),
            additional_symbols={},
            additional_symbol_references=[]
        )

    def _test(self,
              text_printed_by_program: str,
              expected_file_contents: str,
              make_arguments: Callable[[TransformableContentsConstructor], ArgumentElements],
              additional_symbols: Dict[str, SymbolContainer],
              additional_symbol_references: List[asrt.ValueAssertion[SymbolReference]],
              ):
        expected_file = fs.File('a-file-name.txt', expected_file_contents)

        for proc_output_file in ProcOutputFile:
            python_source = py_programs.single_line_pgm_that_prints_to(proc_output_file,
                                                                       text_printed_by_program)

            program_that_executes_py_source_symbol = NameAndValue(
                'PROGRAM_THAT_EXECUTES_PY_SOURCE',
                program_resolvers.for_py_source_on_command_line(python_source)
            )

            symbols_dict = {
                program_that_executes_py_source_symbol.name:
                    symbol_utils.container(program_that_executes_py_source_symbol.value),
            }
            symbols_dict.update(additional_symbols)
            symbols = SymbolTable(symbols_dict)

            program_cases = [
                ProgramCase('executable file',
                            pgm_args.interpret_py_source_elements(python_source),
                            []
                            ),
                ProgramCase('symbol reference program',
                            arg.elements([
                                pgm_args.symbol_ref_command_line(sym_ref_args.sym_ref_cmd_line(
                                    program_that_executes_py_source_symbol.name))
                            ]),
                            [asrt_pgm.is_program_reference_to(program_that_executes_py_source_symbol.name)]
                            ),
            ]

            for program_case in program_cases:
                program_contents_constructor = TransformableContentsConstructor(
                    output_from_program(proc_output_file, program_case.source)
                )
                program_contents_arguments = make_arguments(program_contents_constructor)

                rel_opt_conf = AN_ALLOWED_DST_FILE_RELATIVITY

                source = arg.elements([rel_opt_conf.file_argument_with_option(expected_file.name)]) \
                    .followed_by(program_contents_arguments) \
                    .as_remaining_source

                expected_symbol_references = program_case.expected_references + additional_symbol_references

                with self.subTest(relativity_option_string=str(rel_opt_conf.option_argument),
                                  program=program_case.name,
                                  remaining_source=source.remaining_source,
                                  output_channel=proc_output_file):
                    self._check(
                        source,
                        ArrangementWithSds(
                            symbols=symbols,
                        ),
                        Expectation(
                            main_result=IS_SUCCESS,
                            side_effects_on_home=f_asrt.dir_is_empty(),
                            symbol_usages=asrt.matches_sequence(expected_symbol_references),
                            main_side_effects_on_sds=non_home_dir_contains_exactly(rel_opt_conf.root_dir__non_home,
                                                                                   fs.DirContents([expected_file])),
                        ))


class TestSuccessfulScenariosWithDifferentSourceVariants(TestCaseBase):
    def test_contents_from_stdout_with_transformer(self):
        text_printed_by_program = 'single line of output'
        expected_file_contents = text_printed_by_program.upper() + '\n'
        file_arg = RelOptFileRefArgument('a-file-name.txt', RelOptionType.REL_TMP)

        expected_file = fs.File(file_arg.name, expected_file_contents)

        to_upper_transformer = NameAndValue('TO_UPPER_CASE',
                                            StringTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        symbols = SymbolTable({
            to_upper_transformer.name: container(to_upper_transformer.value)
        })

        program_cases = [
            NameAndValue(
                'executable file',
                pgm_args.program(pgm_args.interpret_py_source_line(
                    py_programs.single_line_pgm_that_prints_to_stdout_with_new_line(text_printed_by_program)),
                    transformation=to_upper_transformer.name
                )
            ),
            NameAndValue(
                'shell command line',
                pgm_args.program(pgm_args.shell_command_line(
                    command_that_prints_line_to_stdout(text_printed_by_program)),
                    transformation=to_upper_transformer.name
                )
            ),
        ]

        source_cases = [
            NIE('no following lines',
                asrt_source.source_is_at_end,
                []
                ),
            NIE('empty following line',
                asrt_source.is_at_beginning_of_line(4),
                ['',
                 '   following line with text']
                ),
            NIE('with following lines',
                asrt_source.is_at_beginning_of_line(3),
                ['following line']
                ),
        ]
        for source_case in source_cases:
            for program_case in program_cases:
                program_contents_arguments = TransformableContentsConstructor(
                    output_from_program(ProcOutputFile.STDOUT, program_case.value)
                ).without_transformation().as_arguments

                source = remaining_source(
                    '{file_arg} {program_contents_arguments}'.format(
                        file_arg=file_arg,
                        program_contents_arguments=program_contents_arguments.first_line),
                    program_contents_arguments.following_lines + source_case.input_value)

                with self.subTest(program=program_case.name,
                                  following_source=source_case.name,
                                  remaining_source=source.remaining_source):
                    self._check(
                        source,
                        ArrangementWithSds(
                            pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                            symbols=symbols
                        ),
                        Expectation(
                            main_result=IS_SUCCESS,
                            side_effects_on_home=f_asrt.dir_is_empty(),
                            symbol_usages=asrt.matches_sequence([
                                is_reference_to_lines_transformer(to_upper_transformer.name),
                            ]),
                            main_side_effects_on_sds=dir_contains_exactly(file_arg.relativity_option,
                                                                          fs.DirContents([expected_file])),
                            source=source_case.expected_value
                        ))


class TestFailingValidation(TestCaseBase):
    def test_validation_of_non_existing_file_pre_sds_fails(self):
        # ARRANGE #
        program_with_ref_to_file_in_home_ds = pgm_args.program(
            pgm_args.interpret_py_source_file(ab.file_ref_rel_opt('non-existing-file',
                                                                  RelOptionType.REL_HOME_CASE))
        )
        complete_arguments = instr_args.from_program('dst-file.txt',
                                                     ProcOutputFile.STDOUT,
                                                     program_with_ref_to_file_in_home_ds)
        # ACT & ASSERT #
        self._check(complete_arguments.as_remaining_source,
                    ArrangementWithSds(),
                    Expectation(validation_pre_sds=asrt.is_instance(str)))

    def test_validation_of_non_existing_file_post_sds_fails(self):
        # ARRANGE #
        program_with_ref_to_file_in_home_ds = pgm_args.program(
            pgm_args.interpret_py_source_file(ab.file_ref_rel_opt('non-existing-file',
                                                                  RelOptionType.REL_ACT))
        )
        complete_arguments = instr_args.from_program('dst-file.txt',
                                                     ProcOutputFile.STDOUT,
                                                     program_with_ref_to_file_in_home_ds)
        # ACT & ASSERT #
        self._check(complete_arguments.as_remaining_source,
                    ArrangementWithSds(),
                    Expectation(validation_post_sds=asrt.is_instance(str)))


class TestFailingScenarios(TestCaseBase):
    def _expect_failure(self, failing_program_as_single_line: Stringable):
        failing_program = ArgumentElements([failing_program_as_single_line])
        transformer = NameAndValue('TRANSFORMER',
                                   StringTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        symbols = SymbolTable({
            transformer.name: container(transformer.value)
        })

        cases = [
            NameAndValue('without transformer',
                         None),
            NameAndValue('with transformer',
                         transformer.name),
        ]
        for case in cases:
            source = instr_args.from_program('dst-file.txt',
                                             ProcOutputFile.STDOUT,
                                             failing_program,
                                             transformation=case.value).as_remaining_source

            with self.subTest(case.name):
                self._check(
                    source,
                    ArrangementWithSds(
                        symbols=symbols,
                    ),
                    Expectation(
                        symbol_usages=asrt.anything_goes(),
                        main_result=IS_FAILURE,
                    ))

    def test_WHEN_exitcode_from_shell_command_is_non_zero_THEN_result_SHOULD_be_error_message(self):
        self._expect_failure(
            pgm_args.shell_command_line(shell_commands.command_that_exits_with_code(1))
        )

    def test_WHEN_shell_command_is_non_executable_THEN_result_SHOULD_be_error_message(self):
        non_executable_shell_command = '<'
        self._expect_failure(
            pgm_args.shell_command_line(non_executable_shell_command)
        )


class TestCommonFailingScenariosDueToInvalidDestinationFile(TestCommonFailingScenariosDueToInvalidDestinationFileBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        arbitrary_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                             StringTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))

        symbols = SymbolTable({
            arbitrary_transformer.name: container(arbitrary_transformer.value),
        })

        shell_contents_arguments_constructor = TransformableContentsConstructor(
            output_from_program(ProcOutputFile.STDOUT,
                                pgm_args.shell_command(shell_commands.command_that_exits_with_code(0))
                                )
        )

        file_contents_cases = [
            NameAndValue(
                'contents of output from shell command / without transformation',
                shell_contents_arguments_constructor.without_transformation()
            ),
            NameAndValue(
                'contents of output from shell command / with transformation',
                shell_contents_arguments_constructor.with_transformation(arbitrary_transformer.name)
            ),
        ]

        return InvalidDestinationFileTestCasesData(
            file_contents_cases,
            symbols)
