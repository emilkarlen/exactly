import unittest
from typing import List, Callable, Dict, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.instructions.multi_phase import new_file as sut
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType
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
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import path_arguments
from exactly_lib_test.tcfs.test_resources.path_arguments import RelOptPathArgument
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    non_hds_dir_contains_exactly, dir_contains_exactly
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.parse.test_resources import arguments_building as arg
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.test_case_utils.program.test_resources import command_cmd_line_args as sym_ref_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.programs.shell_commands import command_that_prints_line_to_stdout
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformers import \
    to_uppercase
from exactly_lib_test.type_val_deps.types.path.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext, \
    NON_EXISTING_SYSTEM_PROGRAM


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
        unittest.makeSuite(TestFailDueInvalidSyntax),
        unittest.makeSuite(TestUnableToExecute),
        unittest.makeSuite(TestNonZeroExitCode),
        unittest.makeSuite(TestSuccessfulScenariosWithDifferentSourceVariants),
        unittest.makeSuite(TestSuccessfulScenariosWithProgramFromDifferentChannels),
        unittest.makeSuite(TestSymbolUsages),
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

                source = arg.elements([rel_opt_conf.path_argument_of_rel_name(expected_file.name)]) \
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
                asrt_source.is_at_beginning_of_line(3),
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
            pgm_args.interpret_py_source_file(path_arguments.RelOptPathArgument('non-existing-file',
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
            pgm_args.interpret_py_source_file(path_arguments.RelOptPathArgument('non-existing-file',
                                                                                RelOptionType.REL_ACT))
        )
        complete_arguments = instr_args.from_program('dst-file.txt',
                                                     ProcOutputFile.STDOUT,
                                                     program_with_ref_to_file_in_hds_ds)
        # ACT & ASSERT #
        self._check(complete_arguments.as_remaining_source,
                    ArrangementWithSds(),
                    embryo_check.expectation(validation=validation.post_sds_validation_fails__w_any_msg()))


class TestUnableToExecute(TestCaseBase):
    def test_WHEN_program_is_non_non_existing_system_command_THEN_result_SHOULD_be_error_message(self):
        failing_program = pgm_args.system_program_argument_elements(NON_EXISTING_SYSTEM_PROGRAM)
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
            source = instr_args.from_program(
                'dst-file.txt',
                ProcOutputFile.STDOUT,
                failing_program,
                transformation=case.value,
            ).as_remaining_source

            with self.subTest(case.name):
                self._check(
                    source,
                    ArrangementWithSds(
                        symbols=symbols,
                    ),
                    Expectation(
                        source=asrt_source.source_is_at_end,
                        symbol_usages=asrt.anything_goes(),
                        main_result=IS_FAILURE,
                    ))


class TestNonZeroExitCode(TestCaseBase):
    def test_result_SHOULD_be_failure_WHEN_non_zero_exit_code_and_exit_code_is_not_ignored(self):
        self._check_exit_codes(
            exit_code_cases=[1, 69],
            ignore_exit_code=False,
            main_result=IS_FAILURE,
            expected_output_dir_contents=self._dir_is_empty
        )

    def test_result_SHOULD_be_success_WHEN_any_zero_exit_code_and_exit_code_is_ignored(self):
        self._check_exit_codes(
            exit_code_cases=[0, 1, 2, 69],
            ignore_exit_code=True,
            main_result=IS_SUCCESS,
            expected_output_dir_contents=self._dir_contains_exactly_created_file,
        )

    def _check_exit_codes(self,
                          exit_code_cases: List[int],
                          ignore_exit_code: bool,
                          main_result: ValueAssertion[Optional[TextRenderer]],
                          expected_output_dir_contents: Callable[[str, str], DirContents],
                          ):
        # ARRANGE #
        destination_file_name = 'dst-file.txt'

        program_output = {
            ProcOutputFile.STDOUT: 'output on stdout',
            ProcOutputFile.STDERR: 'output on stderr',
        }
        transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER',
            to_uppercase(),
        )

        py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)

        transformer_cases = [
            NameAndValue('without transformer',
                         None),
            NameAndValue('with transformer',
                         transformer.name),
        ]

        for output_file in ProcOutputFile:
            for exit_code in exit_code_cases:
                py_file = File('exit-with-hard-coded-exit-code.py',
                               py_programs.py_pgm_with_stdout_stderr_exit_code(
                                   exit_code=exit_code,
                                   stdout_output=program_output[ProcOutputFile.STDOUT],
                                   stderr_output=program_output[ProcOutputFile.STDERR],
                               ),
                               )

                py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

                program_symbol = ProgramSymbolContext.of_sdv(
                    'PROGRAM_SYMBOL_NAME',
                    program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
                )
                symbol_contexts = [program_symbol, transformer]

                for transformer_case in transformer_cases:
                    with self.subTest(exit_code=exit_code):
                        # ACT && ASSERT #
                        self._check(
                            source=instr_args.from_program(
                                destination_file_name,
                                output_file,
                                program=pgm_args.symbol_ref_command_elements(program_symbol.name),
                                ignore_exit_code=ignore_exit_code,
                                transformation=transformer_case.value,
                            ).as_remaining_source,
                            arrangement=ArrangementWithSds(
                                symbols=SymbolContext.symbol_table_of_contexts(symbol_contexts),
                                tcds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                                    DirContents([py_file])
                                )
                            ),
                            expectation=
                            Expectation(
                                source=asrt_source.source_is_at_end,
                                symbol_usages=program_symbol.references_assertion,
                                main_result=main_result,
                                main_side_effects_on_sds=dir_contains_exactly(
                                    RelOptionType.REL_ACT,
                                    expected_output_dir_contents(
                                        destination_file_name, program_output[output_file])
                                )
                            ),
                        )

    @staticmethod
    def _dir_is_empty(file_name: str, contents_on_output_channel: str) -> DirContents:
        return DirContents.empty()

    @staticmethod
    def _dir_contains_exactly_created_file(file_name: str, contents_on_output_channel: str) -> DirContents:
        return DirContents([File(file_name, contents_on_output_channel)])


class TestCommonFailingScenariosDueToInvalidDestinationFile(
    TestCommonFailingScenariosDueToInvalidDestinationFileBase):
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


class TestFailDueInvalidSyntax(TestCaseBase):
    def test_superfluous_arguments(self):
        for phase_is_after_act in [False, True]:
            for output_file in ProcOutputFile:
                for ignore_exit_code in [False, True]:
                    with self.subTest(output_file=output_file,
                                      phase_is_after_act=phase_is_after_act,
                                      ignore_exit_code=ignore_exit_code):
                        source = instr_args.from_program(
                            'dst.txt',
                            output_file,
                            pgm_args.program_w_superfluous_args().as_argument_elements,
                            ignore_exit_code=ignore_exit_code,
                        )
                        parse_source = source.as_remaining_source
                        self._check_invalid_syntax(
                            parse_source,
                            phase_is_after_act,
                        )
