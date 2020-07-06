import unittest
from typing import List, Callable, Dict

from exactly_lib.instructions.multi_phase import new_file as sut
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase.new_file.test_resources import \
    arguments_building as instr_args
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    InvalidDestinationFileTestCasesData, \
    TestCommonFailingScenariosDueToInvalidDestinationFileBase
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    TestCaseBase
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.utils import \
    IS_FAILURE, IS_SUCCESS, AN_ALLOWED_DST_FILE_RELATIVITY
from exactly_lib_test.instructions.multi_phase.test_resources import instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.parse_file_maker import \
    TransformableContentsConstructor, output_from_program
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_file_structure.test_resources.arguments_building import RelOptPathArgument
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    non_hds_dir_contains_exactly, dir_contains_exactly
from exactly_lib_test.test_case_utils.parse.test_resources import arguments_building as arg
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import command_cmd_line_args as sym_ref_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.programs.shell_commands import command_that_prints_line_to_stdout
from exactly_lib_test.test_resources.strings import WithToString
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformers import \
    to_uppercase


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
        text_printed_by_shell_command_symbol = StringSymbolContext.of_constant('STRING_TO_PRINT_SYMBOL', 'hello_world')

        dst_file_symbol = ConstantSuffixPathDdvSymbolContext(
            'DST_FILE_SYMBOL',
            RelOptionType.REL_ACT,
            'dst-file-name.txt',
            sut.REL_OPT_ARG_CONF.options.accepted_relativity_variants,
        )

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            to_uppercase()
        )

        transformed_shell_contents_arguments = TransformableContentsConstructor(
            output_from_program(ProcOutputFile.STDOUT,
                                pgm_args.shell_command(
                                    shell_commands.command_that_prints_line_to_stdout(
                                        text_printed_by_shell_command_symbol.name__sym_ref_syntax
                                    ))
                                )
        ).with_transformation(to_upper_transformer.name).as_arguments

        source = remaining_source(
            '{file_name} {content_arguments}'.format(
                file_name=dst_file_symbol.name__sym_ref_syntax,
                content_arguments=transformed_shell_contents_arguments.first_line
            ),
            transformed_shell_contents_arguments.following_lines)

        symbols = SymbolContext.symbol_table_of_contexts([
            dst_file_symbol,
            text_printed_by_shell_command_symbol,
            to_upper_transformer,
        ])

        # ACT & ASSERT #

        self._check(source,
                    ArrangementWithSds(
                        symbols=symbols,
                    ),
                    Expectation(
                        main_result=IS_SUCCESS,
                        symbol_usages=asrt.matches_sequence([
                            dst_file_symbol.reference_assertion__path_or_string,
                            text_printed_by_shell_command_symbol.reference_assertion__any_data_type,
                            to_upper_transformer.reference_assertion,
                        ]),
                    )
                    )


class ProgramCase:
    def __init__(self,
                 name: str,
                 source: ArgumentElements,
                 expected_reference: List[ValueAssertion[SymbolReference]]):
        self.name = name
        self.source = source
        self.expected_references = expected_reference


class TestSuccessfulScenariosWithProgramFromDifferentChannels(TestCaseBase):
    def test_with_transformation(self):
        text_printed_by_program = 'the text printed by the program'
        transformer = StringTransformerSymbolContext.of_primitive(
            'TO_UPPER_CASE',
            to_uppercase(),
        )
        self._test(
            text_printed_by_program=text_printed_by_program,
            expected_file_contents=text_printed_by_program.upper(),
            make_arguments=lambda tcc: tcc.with_transformation(transformer.name),
            additional_symbols={transformer.name: transformer.symbol_table_container},
            additional_symbol_references=[transformer.reference_assertion]
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
              additional_symbol_references: List[ValueAssertion[SymbolReference]],
              ):
        expected_file = fs.File('a-file-name.txt', expected_file_contents)

        for proc_output_file in ProcOutputFile:
            python_source = py_programs.single_line_pgm_that_prints_to(proc_output_file,
                                                                       text_printed_by_program)

            program_that_executes_py_source_symbol = ProgramSymbolContext.of_sdv(
                'PROGRAM_THAT_EXECUTES_PY_SOURCE',
                program_sdvs.for_py_source_on_command_line(python_source)
            )

            symbols_dict = {
                program_that_executes_py_source_symbol.name:
                    program_that_executes_py_source_symbol.symbol_table_container,
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
                            [program_that_executes_py_source_symbol.reference_assertion]
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
                            side_effects_on_hds=f_asrt.dir_is_empty(),
                            symbol_usages=asrt.matches_sequence(expected_symbol_references),
                            main_side_effects_on_sds=non_hds_dir_contains_exactly(rel_opt_conf.root_dir__non_hds,
                                                                                  fs.DirContents([expected_file])),
                        ))


class TestSuccessfulScenariosWithDifferentSourceVariants(TestCaseBase):
    def test_contents_from_stdout_with_transformer(self):
        text_printed_by_program = 'single line of output'
        expected_file_contents = text_printed_by_program.upper() + '\n'
        file_arg = RelOptPathArgument('a-file-name.txt', RelOptionType.REL_TMP)

        expected_file = fs.File(file_arg.name, expected_file_contents)

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TO_UPPER_CASE',
            to_uppercase(),
        )
        symbols = to_upper_transformer.symbol_table

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
                            pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                            symbols=symbols
                        ),
                        Expectation(
                            main_result=IS_SUCCESS,
                            side_effects_on_hds=f_asrt.dir_is_empty(),
                            symbol_usages=asrt.matches_sequence([
                                to_upper_transformer.reference_assertion,
                            ]),
                            main_side_effects_on_sds=dir_contains_exactly(file_arg.relativity_option,
                                                                          fs.DirContents([expected_file])),
                            source=source_case.expected_value
                        ))


class TestFailingValidation(TestCaseBase):
    def test_validation_of_non_existing_file_pre_sds_fails(self):
        # ARRANGE #
        program_with_ref_to_file_in_hds_ds = pgm_args.program(
            pgm_args.interpret_py_source_file(ab.path_rel_opt('non-existing-file',
                                                              RelOptionType.REL_HDS_CASE))
        )
        complete_arguments = instr_args.from_program('dst-file.txt',
                                                     ProcOutputFile.STDOUT,
                                                     program_with_ref_to_file_in_hds_ds)
        # ACT & ASSERT #
        self._check(complete_arguments.as_remaining_source,
                    ArrangementWithSds(),
                    embryo_check.expectation(validation=validation.pre_sds_validation_fails__w_any_msg()))

    def test_validation_of_non_existing_file_post_sds_fails(self):
        # ARRANGE #
        program_with_ref_to_file_in_hds_ds = pgm_args.program(
            pgm_args.interpret_py_source_file(ab.path_rel_opt('non-existing-file',
                                                              RelOptionType.REL_ACT))
        )
        complete_arguments = instr_args.from_program('dst-file.txt',
                                                     ProcOutputFile.STDOUT,
                                                     program_with_ref_to_file_in_hds_ds)
        # ACT & ASSERT #
        self._check(complete_arguments.as_remaining_source,
                    ArrangementWithSds(),
                    embryo_check.expectation(validation=validation.post_sds_validation_fails__w_any_msg()))


class TestFailingScenarios(TestCaseBase):
    def _expect_failure(self, failing_program_as_single_line: WithToString):
        failing_program = ArgumentElements([failing_program_as_single_line])
        transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER',
            to_uppercase(),
        )
        symbols = transformer.symbol_table

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
        arbitrary_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            to_uppercase(),
        )

        symbols = arbitrary_transformer.symbol_table

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
