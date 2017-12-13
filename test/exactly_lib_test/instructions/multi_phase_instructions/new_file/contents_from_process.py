import unittest

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.multi_phase_instructions import new_file as sut
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.data.string_resolver import string_constant
from exactly_lib.symbol.data.value_resolvers.file_ref_resolvers import resolver_of_rel_option
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelNonHomeOptionType
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase_instructions.new_file.test_resources import TestCaseBase, \
    IS_SUCCESS, ALLOWED_DST_FILE_RELATIVITIES, IS_FAILURE, \
    Arguments
from exactly_lib_test.instructions.multi_phase_instructions.new_file.test_resources import \
    stdout_from, shell_command, TransformableContentsConstructor, \
    InvalidDestinationFileTestCasesData, \
    TestCommonFailingScenariosDueToInvalidDestinationFileBase
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_not_at_end
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    equals_data_type_reference_restrictions
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.symbol.test_resources.lines_transformer import LinesTransformerResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.lines_transformer import is_lines_transformer_reference_to
from exactly_lib_test.symbol.test_resources.resolver_structure_assertions import matches_reference_2
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    non_home_dir_contains_exactly
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.test_transformers import \
    MyToUppercaseTransformer
from exactly_lib_test.test_case_utils.parse.parse_file_ref import file_ref_or_string_reference_restrictions
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_non_home
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.programs.shell_commands import command_that_prints_line_to_stdout
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, file_assertions as f_asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestScenariosWithContentsFromProcessOutput),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
    ])


class TestScenariosWithContentsFromProcessOutput(TestCaseBase):
    TRANSFORMER_OPTION = option_syntax(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME)

    def test_symbol_usages(self):
        # ARRANGE #
        text_printed_by_shell_command_symbol = NameAndValue('STRING_TO_PRINT_SYMBOL', 'hello_world')

        dst_file_symbol = NameAndValue('DST_FILE_SYMBOL', 'dst-file-name.txt')

        to_upper_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))

        transformed_shell_contents_arguments = TransformableContentsConstructor(
            stdout_from(
                shell_command(shell_commands.command_that_prints_line_to_stdout(
                    symbol_reference_syntax_for_name(text_printed_by_shell_command_symbol.name)
                ))
            )
        ).with_transformation(to_upper_transformer.name)

        source = remaining_source(
            '{file_name} {content_arguments}'.format(
                file_name=symbol_reference_syntax_for_name(dst_file_symbol.name),
                content_arguments=transformed_shell_contents_arguments.first_line
            ),
            transformed_shell_contents_arguments.following_lines)

        symbols = SymbolTable({
            dst_file_symbol.name:
                container(resolver_of_rel_option(RelOptionType.REL_ACT,
                                                 PathPartAsFixedPath(dst_file_symbol.value))),

            to_upper_transformer.name:
                container(to_upper_transformer.value),

            text_printed_by_shell_command_symbol.name:
                container(string_constant(text_printed_by_shell_command_symbol.value))
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

                            is_lines_transformer_reference_to(to_upper_transformer.name),

                            matches_reference_2(
                                text_printed_by_shell_command_symbol.name,
                                equals_data_type_reference_restrictions(is_any_data_type())),
                        ]),
                    )
                    )

    def test_contents_from_stdout_of_shell_command__without_transformer(self):
        text_printed_by_shell_command = 'single line of output'
        expected_file_contents = text_printed_by_shell_command + '\n'
        expected_file = fs.File('a-file-name.txt', expected_file_contents)

        shell_contents_arguments = TransformableContentsConstructor(
            stdout_from(
                shell_command(command_that_prints_line_to_stdout(text_printed_by_shell_command))
            )
        ).without_transformation()

        for rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                self._check(
                    remaining_source(
                        '{rel_opt} {file_name} {contents_arguments}'.format(
                            rel_opt=rel_opt_conf.option_string,
                            file_name=expected_file.file_name,
                            contents_arguments=shell_contents_arguments.first_line
                        ),
                        shell_contents_arguments.following_lines),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                    ),
                    Expectation(
                        main_result=IS_SUCCESS,
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_list,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(rel_opt_conf.root_dir__non_home,
                                                                               fs.DirContents([expected_file])),
                    ))

    def test_contents_from_stdout_of_shell_command__with_transformer(self):
        text_printed_by_shell_command = 'single line of output'
        expected_file_contents = text_printed_by_shell_command.upper() + '\n'
        expected_file = fs.File('a-file-name.txt', expected_file_contents)
        to_upper_transformer = NameAndValue('TO_UPPER_CASE',
                                            LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        symbols = SymbolTable({
            to_upper_transformer.name: container(to_upper_transformer.value)
        })

        rel_opt_conf = conf_rel_non_home(RelNonHomeOptionType.REL_TMP)

        shell_contents_arguments = TransformableContentsConstructor(
            stdout_from(
                shell_command(command_that_prints_line_to_stdout(text_printed_by_shell_command))
            )
        ).with_transformation(to_upper_transformer.name)

        self._check(
            remaining_source(
                '{rel_opt} {file_name} {shell_contents_arguments}'.format(
                    rel_opt=rel_opt_conf.option_string,
                    file_name=expected_file.file_name,
                    shell_contents_arguments=shell_contents_arguments.first_line,
                ),
                shell_contents_arguments.following_lines),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                symbols=symbols
            ),
            Expectation(
                main_result=IS_SUCCESS,
                side_effects_on_home=f_asrt.dir_is_empty(),
                symbol_usages=asrt.matches_sequence([
                    is_lines_transformer_reference_to(to_upper_transformer.name),
                ]),
                main_side_effects_on_sds=non_home_dir_contains_exactly(rel_opt_conf.root_dir__non_home,
                                                                       fs.DirContents([expected_file])),
            ))

    def test_WHEN_exitcode_from_shell_command_is_non_zero_THEN_result_SHOULD_be_error_message(self):
        transformer = NameAndValue('TRANSFORMER',
                                   LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        symbols = SymbolTable({
            transformer.name: container(transformer.value)
        })
        shell_contents_arguments = TransformableContentsConstructor(
            stdout_from(
                shell_command(shell_commands.command_that_exits_with_code(1))
            )
        )

        cases = [
            NameAndValue('without transformer',
                         shell_contents_arguments.without_transformation()),
            NameAndValue('with transformer',
                         shell_contents_arguments.with_transformation(transformer.name)),
        ]
        for case in cases:
            with self.subTest(case.name):
                self._check(
                    remaining_source(
                        '{file_name} {shell_command_with_non_zero_exit_code}'.format(
                            file_name='dst-file-name.txt',
                            shell_command_with_non_zero_exit_code=case.value.first_line,
                        ),
                        case.value.following_lines),
                    ArrangementWithSds(
                        symbols=symbols,
                    ),
                    Expectation(
                        symbol_usages=asrt.anything_goes(),
                        main_result=IS_FAILURE,
                    ))

    def test_new_line_before_mandatory_arguments_SHOULD_be_accepted(self):
        # ARRANGE #

        identity_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            LinesTransformerResolverConstantTestImpl(IdentityLinesTransformer()))

        symbols = SymbolTable({
            identity_transformer.name: container(identity_transformer.value),
        })

        text_to_print = 'text to print'
        expected_dst_file = fs.File('dst-file.txt', text_to_print + '\n')

        dst_file_rel_opt_conf = conf_rel_non_home(RelNonHomeOptionType.REL_ACT)
        assertion_on_non_home_contents = dst_file_rel_opt_conf.assert_root_dir_contains_exactly(
            fs.DirContents([expected_dst_file]))

        shell_contents_arguments_constructor = TransformableContentsConstructor(
            stdout_from(
                shell_command(shell_commands.command_that_prints_line_to_stdout(text_to_print)),
                with_new_line_after_output_option=True,
            ),
            with_new_line_after_transformer=True,
        )

        file_contents_cases = [
            NameAndValue(
                'without transformation',
                shell_contents_arguments_constructor.without_transformation()
            ),
            NameAndValue(
                'with transformation',
                shell_contents_arguments_constructor.with_transformation(identity_transformer.name)
            ),
        ]

        text_on_line_after_instruction = ' text on line after instruction'

        for file_contents_case in file_contents_cases:
            optional_arguments = file_contents_case.value
            assert isinstance(optional_arguments, Arguments)  # Type info for IDE

            with self.subTest(file_contents_variant=file_contents_case.name,
                              first_line_argments=optional_arguments.first_line):
                source = remaining_source(
                    '{rel_opt} {dst_file_name} {optional_arguments}'.format(
                        rel_opt=dst_file_rel_opt_conf.option_string,
                        dst_file_name=expected_dst_file.name,
                        optional_arguments=optional_arguments.first_line,
                    ),
                    optional_arguments.following_lines +
                    [text_on_line_after_instruction]
                )

                # ACT & ASSERT #

                self._check(source,
                            ArrangementWithSds(
                                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                                symbols=symbols,
                            ),
                            Expectation(
                                main_result=IS_SUCCESS,
                                symbol_usages=asrt.anything_goes(),
                                main_side_effects_on_sds=assertion_on_non_home_contents,
                                source=source_is_not_at_end(
                                    remaining_part_of_current_line=asrt.equals(text_on_line_after_instruction)
                                )

                            )
                            )


class TestCommonFailingScenariosDueToInvalidDestinationFile(TestCommonFailingScenariosDueToInvalidDestinationFileBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        arbitrary_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                             LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))

        symbols = SymbolTable({
            arbitrary_transformer.name: container(arbitrary_transformer.value),
        })

        shell_contents_arguments_constructor = TransformableContentsConstructor(
            stdout_from(
                shell_command(shell_commands.command_that_exits_with_code(0))
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
