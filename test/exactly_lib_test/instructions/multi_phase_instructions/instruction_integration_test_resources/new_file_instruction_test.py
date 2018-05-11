import unittest

from exactly_lib.instructions.multi_phase_instructions import new_file
from exactly_lib.instructions.utils.parse import parse_file_maker
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.phases.common import TestCaseInstructionWithSymbols
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelHomeOptionType, RelNonHomeOptionType
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_documentation_instance
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.instructions.utils.parse.parse_file_maker.test_resources import arguments
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.symbol.test_resources.lines_transformer import is_reference_to_lines_transformer, \
    StringTransformerResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    non_home_dir_contains_exactly
from exactly_lib_test.test_case_utils.parse.parse_file_ref import file_ref_or_string_reference_restrictions
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_arguments
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_any, conf_rel_home, \
    conf_rel_non_home
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.file_structure import DirContents
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.programs.shell_commands import command_that_prints_line_to_stdout, \
    command_that_exits_with_code
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.string_transformers import \
    MyToUppercaseTransformer


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    common_test_cases = [
        TestSymbolUsages,
        TestContentsFromExistingFile_Successfully,

        TestContentsFromOutputOfShellCommand_Successfully,

        TestValidationErrorPreSds_DueTo_NonExistingSourceFile,
        TestHardError_DueTo_NonZeroExitCodeFromShellCommand,
    ]
    suites = [tc(conf)
              for tc in common_test_cases
              ]

    if conf.phase_is_after_act():
        suites.append(TestParseShouldSucceedWhenRelativityOfSourceIsRelResult(conf))
    else:
        suites.append(TestParseShouldFailWhenRelativityOfSourceIsRelResult(conf))

    suites.append(suite_for_documentation_instance(conf.documentation()))

    return unittest.TestSuite(suites)


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: ConfigurationBase):
        super().__init__()
        self.conf = conf

    def shortDescription(self):
        return '\n / '.join([str(type(self)),
                             str(type(self.conf))])


class TestSymbolUsages(TestCaseBase):
    def runTest(self):
        to_upper_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            StringTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))

        src_file = fs.File('src-file.txt', 'contents of source file')
        src_file_symbol = NameAndValue('SRC_FILE_SYMBOL', src_file.name)

        expected_dst_file = fs.File('dst-file-name.txt', src_file.contents.upper())
        dst_file_symbol = NameAndValue('DST_FILE_SYMBOL', expected_dst_file.name)

        file_contents_arg = arguments.TransformableContentsConstructor(
            arguments.file_with_rel_opt_conf(symbol_reference_syntax_for_name(src_file_symbol.name))
        ).with_transformation(to_upper_transformer.name).as_arguments

        source = remaining_source(
            '{file_name} {content_arguments}'.format(
                file_name=symbol_reference_syntax_for_name(dst_file_symbol.name),
                content_arguments=file_contents_arg.first_line
            ),
            file_contents_arg.following_lines)

        # ACT #

        instruction = self.conf.parser().parse(source)
        assert isinstance(instruction, TestCaseInstructionWithSymbols)  # Sanity check

        # ASSERT #

        expected_symbol_usages = [

            equals_symbol_reference(
                SymbolReference(dst_file_symbol.name,
                                file_ref_or_string_reference_restrictions(
                                    new_file.REL_OPT_ARG_CONF.options.accepted_relativity_variants))
            ),

            is_reference_to_lines_transformer(to_upper_transformer.name),

            equals_symbol_reference(
                SymbolReference(src_file_symbol.name,
                                file_ref_or_string_reference_restrictions(
                                    parse_file_maker._src_rel_opt_arg_conf_for_phase(
                                        self.conf.phase_is_after_act()).options.accepted_relativity_variants))
            ),
        ]
        expected_symbol_references = asrt.matches_sequence(expected_symbol_usages)
        expected_symbol_references.apply_without_message(self,
                                                         instruction.symbol_usages())


class TestParseShouldFailWhenRelativityOfSourceIsRelResult(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        instruction_arguments = instruction_arguments_for_src_file_rel_result()

        source = remaining_source(instruction_arguments)
        # ACT #
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            # ACT #
            self.conf.parser().parse(source)


class TestParseShouldSucceedWhenRelativityOfSourceIsRelResult(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        instruction_arguments = instruction_arguments_for_src_file_rel_result()

        source = remaining_source(instruction_arguments)
        # ACT #
        self.conf.parser().parse(source)


def instruction_arguments_for_src_file_rel_result() -> str:
    src_file_arg = PathArgumentWithRelativity('src-file.txt',
                                              conf_rel_any(RelOptionType.REL_RESULT))
    dst_file_arg = PathArgumentWithRelativity('dst-file.txt',
                                              conf_rel_any(RelOptionType.REL_ACT))
    contents_arg = arguments.TransformableContentsConstructor(
        arguments.file_with_rel_opt_conf(src_file_arg.file_name, src_file_arg.relativity)
    ).without_transformation().as_arguments

    return '{dst_file_arg} {contents_arguments}'.format(
        dst_file_arg=dst_file_arg.argument_str,
        contents_arguments=contents_arg.first_line
    )


class TestContentsFromExistingFile_Successfully(TestCaseBase):
    def runTest(self):
        # ARRANGE #

        src_file = fs.File('source-file.txt', 'contents of source file')
        src_rel_opt_conf = conf_rel_home(RelHomeOptionType.REL_HOME_CASE)

        expected_file = fs.File('a-file-name.txt', src_file.contents.upper())
        dst_rel_opt_conf = conf_rel_non_home(RelNonHomeOptionType.REL_ACT)

        to_upper_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            StringTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        symbols = SymbolTable({
            to_upper_transformer.name:
                container(to_upper_transformer.value),
        })

        file_contents_arg = arguments.TransformableContentsConstructor(
            arguments.file_with_rel_opt_conf(src_file.name, src_rel_opt_conf)
        ).with_transformation(to_upper_transformer.name).as_arguments

        expected_non_home_contents = dst_rel_opt_conf.assert_root_dir_contains_exactly(fs.DirContents([expected_file]))

        instruction_arguments = '{rel_opt} {file_name} {contents_arguments}'.format(
            rel_opt=dst_rel_opt_conf.option_argument,
            file_name=expected_file.file_name,
            contents_arguments=file_contents_arg.as_single_string
        )

        # ACT & ASSERT #

        for source in equivalent_source_variants__with_source_check(self, instruction_arguments):
            self.conf.run_test(
                self,
                source,
                self.conf.arrangement(
                    pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                    home_or_sds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                        DirContents([src_file])),
                    symbols=symbols,
                ),
                self.conf.expect_success(
                    main_side_effects_on_sds=expected_non_home_contents,
                    symbol_usages=asrt.matches_sequence([
                        is_reference_to_lines_transformer(to_upper_transformer.name),
                    ])
                ))


class TestContentsFromOutputOfShellCommand_Successfully(TestCaseBase):
    def runTest(self):
        text_printed_by_shell_command = 'single line of output'

        expected_file_contents = text_printed_by_shell_command.upper() + '\n'
        expected_file = fs.File('dst-file.txt', expected_file_contents)

        to_upper_transformer = NameAndValue('TO_UPPER_CASE',
                                            StringTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        symbols = SymbolTable({
            to_upper_transformer.name: container(to_upper_transformer.value)
        })

        rel_opt_conf = conf_rel_non_home(RelNonHomeOptionType.REL_TMP)

        shell_contents_arguments = arguments.TransformableContentsConstructor(
            arguments.output_from_program(
                ProcOutputFile.STDOUT,
                pgm_arguments.shell_command(command_that_prints_line_to_stdout(text_printed_by_shell_command))
            )
        ).with_transformation(to_upper_transformer.name).as_arguments

        instruction_arguments = '{rel_opt} {file_name} {shell_contents_arguments}'.format(
            rel_opt=rel_opt_conf.option_argument,
            file_name=expected_file.file_name,
            shell_contents_arguments=shell_contents_arguments.as_single_string,
        )

        for source in equivalent_source_variants__with_source_check(self, instruction_arguments):
            self.conf.run_test(
                self,
                source,
                self.conf.arrangement(
                    pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                    symbols=symbols
                ),
                self.conf.expect_success(
                    symbol_usages=asrt.matches_sequence([
                        is_reference_to_lines_transformer(to_upper_transformer.name),
                    ]),
                    main_side_effects_on_sds=non_home_dir_contains_exactly(rel_opt_conf.root_dir__non_home,
                                                                           fs.DirContents([expected_file])),
                ))


class TestHardError_DueTo_NonZeroExitCodeFromShellCommand(TestCaseBase):
    def runTest(self):
        shell_contents_arguments = arguments.TransformableContentsConstructor(
            arguments.output_from_program(
                ProcOutputFile.STDOUT,
                pgm_arguments.shell_command(command_that_exits_with_code(1))
            )
        )

        shell_command_arguments = shell_contents_arguments.without_transformation().as_arguments
        instruction_arguments = '{file_name} {shell_command_with_non_zero_exit_code}'.format(
            file_name='dst-file-name.txt',
            shell_command_with_non_zero_exit_code=shell_command_arguments.first_line,
        )

        for source in equivalent_source_variants__with_source_check(self, instruction_arguments):
            self.conf.run_test(
                self,
                source,
                self.conf.arrangement(),
                self.conf.expect_hard_error_of_main(),
            )


class TestValidationErrorPreSds_DueTo_NonExistingSourceFile(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        dst_file = PathArgumentWithRelativity('dst-file.txt',
                                              conf_rel_any(RelOptionType.REL_TMP))

        src_file_rel_conf = conf_rel_home(RelHomeOptionType.REL_HOME_CASE)
        src_file = PathArgumentWithRelativity('non-existing-source-file.txt',
                                              src_file_rel_conf)

        contents_argument = arguments.TransformableContentsConstructor(
            arguments.file_with_rel_opt_conf(src_file.file_name, src_file.relativity)
        ).without_transformation().as_arguments

        instruction_arguments = '{rel_opt} {file_name} {contents_arguments}'.format(
            rel_opt=dst_file.relativity.option_argument,
            file_name=dst_file.file_name,
            contents_arguments=contents_argument.first_line,
        )
        for source in equivalent_source_variants__with_source_check(self, instruction_arguments):
            # ACT & ASSERT#
            self.conf.run_test(
                self,
                source,
                arrangement=
                self.conf.arrangement(),
                expectation=
                self.conf.expect_failing_validation_pre_sds()
            )
