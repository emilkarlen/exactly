import unittest

from exactly_lib.instructions.multi_phase_instructions import new_file
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.phases.common import TestCaseInstructionWithSymbols
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelHomeOptionType, RelNonHomeOptionType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase_instructions import transform
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.instructions.multi_phase_instructions.new_file import TransformableContentsConstructor, file
from exactly_lib_test.instructions.test_resources.check_documentation import suite_for_documentation_instance
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.symbol.test_resources.lines_transformer import is_lines_transformer_reference_to, \
    LinesTransformerResolverConstantTestImpl
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.test_transformers import \
    MyToUppercaseTransformer
from exactly_lib_test.test_case_utils.parse.parse_file_ref import file_ref_or_string_reference_restrictions
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_any, conf_rel_home, \
    conf_rel_non_home
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    common_test_cases = [
        TestSymbolUsages,
        # TestFailingValidationPreSds_TODO,
        # TestFailingWhenDestinationFileExists_TODO,
        TestSuccessfullyCreateFileWithContentsFromExistingFile,
    ]
    suites = [tc(conf)
              for tc in common_test_cases]

    # if conf.phase_is_after_act():
    #     suites.append(TestParseShouldSucceedWhenRelativityOfSourceIsRelResult_TODO(conf))
    # else:
    #     suites.append(TestParseShouldFailWhenRelativityOfSourceIsRelResult_TODO(conf))

    suites.append(suite_for_documentation_instance(conf.documentation()))

    return unittest.TestSuite(suites)


class TestCaseBase(unittest.TestCase):
    def __init__(self,
                 conf: ConfigurationBase):
        super().__init__()
        self.conf = conf

    def shortDescription(self):
        return '\n / '.join([str(type(self)),
                             str(type(self.conf))])


class TestSymbolUsages(TestCaseBase):
    def runTest(self):
        to_upper_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))

        src_file = fs.File('src-file.txt', 'contents of source file')
        src_file_symbol = NameAndValue('SRC_FILE_SYMBOL', src_file.name)

        expected_dst_file = fs.File('dst-file-name.txt', src_file.contents.upper())
        dst_file_symbol = NameAndValue('DST_FILE_SYMBOL', expected_dst_file.name)

        file_contents_arg = TransformableContentsConstructor(
            file(symbol_reference_syntax_for_name(src_file_symbol.name))
        ).with_transformation(to_upper_transformer.name)

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

            is_lines_transformer_reference_to(to_upper_transformer.name),

            equals_symbol_reference(
                SymbolReference(src_file_symbol.name,
                                file_ref_or_string_reference_restrictions(
                                    new_file._src_rel_opt_arg_conf_for_phase(
                                        self.conf.phase_is_after_act()).options.accepted_relativity_variants))
            ),
        ]
        expected_symbol_references = asrt.matches_sequence(expected_symbol_usages)
        expected_symbol_references.apply_without_message(self,
                                                         instruction.symbol_usages())


class TestParseShouldFailWhenRelativityOfSourceIsRelResult_TODO(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        src_file_arg = PathArgumentWithRelativity('src-file.txt',
                                                  conf_rel_any(RelOptionType.REL_RESULT))
        dst_file_arg = PathArgumentWithRelativity('dst-file.txt',
                                                  conf_rel_any(RelOptionType.REL_ACT))
        instruction_argument = transform.ArgumentsConstructor(src_file_arg,
                                                              dst_file_arg).construct()
        source = remaining_source(instruction_argument)
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            # ACT #
            self.conf.parser().parse(source)


class TestParseShouldSucceedWhenRelativityOfSourceIsRelResult_TODO(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        src_file_arg = PathArgumentWithRelativity('src-file.txt',
                                                  conf_rel_any(RelOptionType.REL_RESULT))
        dst_file_arg = PathArgumentWithRelativity('dst-file.txt',
                                                  conf_rel_any(RelOptionType.REL_ACT))
        instruction_argument = transform.ArgumentsConstructor(src_file_arg,
                                                              dst_file_arg).construct()
        source = remaining_source(instruction_argument)
        # ACT #
        self.conf.parser().parse(source)


class TestSuccessfullyCreateFileWithContentsFromExistingFile(TestCaseBase):
    def runTest(self):
        # ARRANGE #

        src_file = fs.File('source-file.txt', 'contents of source file')
        src_rel_opt_conf = conf_rel_home(RelHomeOptionType.REL_HOME_CASE)

        expected_file = fs.File('a-file-name.txt', src_file.contents.upper())
        dst_rel_opt_conf = conf_rel_non_home(RelNonHomeOptionType.REL_ACT)

        to_upper_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        symbols = SymbolTable({
            to_upper_transformer.name:
                container(to_upper_transformer.value),
        })

        file_contents_arg = TransformableContentsConstructor(
            file(src_file.name, src_rel_opt_conf)
        ).with_transformation(to_upper_transformer.name)

        expected_non_home_contents = dst_rel_opt_conf.assert_root_dir_contains_exactly(fs.DirContents([expected_file]))

        instruction_arguments = '{rel_opt} {file_name} {contents_arguments}'.format(
            rel_opt=dst_rel_opt_conf.option_string,
            file_name=expected_file.file_name,
            contents_arguments=file_contents_arg.first_line
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
                        is_lines_transformer_reference_to(to_upper_transformer.name),
                    ])
                ))


class TestFailingValidationPreSds_TODO(TestCaseBase):
    def runTest(self):
        non_existing_src_file = PathArgumentWithRelativity('src-file',
                                                           conf_rel_any(RelOptionType.REL_HOME_CASE))
        dst_file = PathArgumentWithRelativity('dst-file',
                                              conf_rel_any(RelOptionType.REL_TMP))
        source = remaining_source(transform.ArgumentsConstructor(non_existing_src_file, dst_file).construct())
        self.conf.run_test(
            self,
            source,
            arrangement=
            self.conf.arrangement(),
            expectation=
            self.conf.expect_failing_validation_pre_sds()
        )


class TestFailingWhenDestinationFileExists_TODO(TestCaseBase):
    def runTest(self):
        src_file_relativity = RelHomeOptionType.REL_HOME_ACT
        src_file_arg = PathArgumentWithRelativity('src-file',
                                                  conf_rel_home(src_file_relativity))
        dst_file_arg = PathArgumentWithRelativity('dst-file',
                                                  conf_rel_any(RelOptionType.REL_TMP))
        source = remaining_source(transform.ArgumentsConstructor(src_file_arg, dst_file_arg).construct())
        self.conf.run_test(
            self,
            source,
            arrangement=
            self.conf.arrangement(
                hds_contents=home_populators.contents_in(
                    src_file_relativity,
                    DirContents([
                        empty_file(src_file_arg.file_name),
                    ])),
                home_or_sds_contents=dst_file_arg.relativity.populator_for_relativity_option_root(
                    DirContents([
                        empty_file(dst_file_arg.file_name),
                    ]))
            ),
            expectation=
            self.conf.expect_hard_error_of_main()
        )
