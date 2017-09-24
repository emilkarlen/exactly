import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import TestCaseInstructionWithSymbols
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelHomeOptionType, RelSdsOptionType
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources.file_contents.contents_transformation import \
    ToUppercaseLinesTransformer
from exactly_lib_test.instructions.multi_phase_instructions import transform
from exactly_lib_test.instructions.multi_phase_instructions.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.instructions.test_resources.check_description import suite_for_documentation_instance
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.named_element.symbol.restrictions.test_resources.concrete_restriction_assertion import \
    equals_symbol_reference_restrictions
from exactly_lib_test.named_element.test_resources.lines_transformer import is_lines_transformer_reference_to
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.named_element.test_resources.resolver_structure_assertions import matches_reference
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import dir_contains_exactly
from exactly_lib_test.test_case_utils.parse.parse_file_ref import file_ref_reference_restrictions
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_any, conf_rel_home, \
    symbol_conf_rel_home, symbol_conf_rel_sds
from exactly_lib_test.test_resources.file_structure import DirContents, File, empty_file
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    common_test_cases = [
        TestSymbolUsages,
        TestFailingValidationPreSds,
        TestFailingWhenDestinationFileExists,
        TestSuccessfullyCreateFileInExistingDirectory,
    ]
    suites = [tc(conf)
              for tc in common_test_cases]

    if conf.phase_is_after_act():
        suites.append(TestParseShouldSucceedWhenRelativityOfSourceIsRelResult(conf))
    else:
        suites.append(TestParseShouldFailWhenRelativityOfSourceIsRelResult(conf))

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
        # ARRANGE #
        src_path_symbol_name = 'src_path_symbol'
        dst_path_symbol_name = 'dst_path_symbol'
        transformer_symbol_name = 'transformer_symbol'

        line_transformer_variants = [
            NameAndValue('no transformer',
                         ('',
                          [])
                         ),
            NameAndValue('reference to transformer symbol',
                         (transformer_symbol_name,
                          [
                              is_lines_transformer_reference_to(transformer_symbol_name)
                          ])
                         ),
        ]
        dst_file_arg = PathArgumentWithRelativity('dst-file',
                                                  symbol_conf_rel_sds(RelSdsOptionType.REL_TMP,
                                                                      dst_path_symbol_name,
                                                                      transform.DST_PATH_RELATIVITY_VARIANTS))
        src_path_rel_variants = transform.src_path_relativity_variants(not self.conf.phase_is_after_act())
        src_file_arg = PathArgumentWithRelativity('src-file',
                                                  symbol_conf_rel_home(RelHomeOptionType.REL_HOME_CASE,
                                                                       src_path_symbol_name,
                                                                       src_path_rel_variants))
        path_symbol_reference_assertions = [
            matches_reference(asrt.equals(src_path_symbol_name),
                              equals_symbol_reference_restrictions(
                                  file_ref_reference_restrictions(src_path_rel_variants))),

            matches_reference(asrt.equals(dst_path_symbol_name),
                              equals_symbol_reference_restrictions(
                                  file_ref_reference_restrictions(transform.DST_PATH_RELATIVITY_VARIANTS))),

        ]
        for line_transformer_case in line_transformer_variants:
            with self.subTest(line_transformer=line_transformer_case.name):
                symbol_reference_assertions = path_symbol_reference_assertions + line_transformer_case.value[1]
                lines_transformer_arg = line_transformer_case.value[0]
                source = remaining_source(transform.ArgumentsConstructor(src_file_arg,
                                                                         dst_file_arg,
                                                                         lines_transformer_arg).construct())
                # ACT #
                instruction = self.conf.parser().parse(source)
                assert isinstance(instruction, TestCaseInstructionWithSymbols)  # Sanity check
                # ASSERT #
                expected_symbol_references = asrt.matches_sequence(symbol_reference_assertions)
                expected_symbol_references.apply_without_message(self,
                                                                 instruction.symbol_usages())


class TestParseShouldFailWhenRelativityOfSourceIsRelResult(TestCaseBase):
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


class TestParseShouldSucceedWhenRelativityOfSourceIsRelResult(TestCaseBase):
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


class TestSuccessfullyCreateFileInExistingDirectory(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        src_file_contents = 'source file contents'
        expected_dst_file_contents = src_file_contents.upper()

        transform_to_uppercase = NameAndValue(
            'to_uppercase_lines_transformer',
            ToUppercaseLinesTransformer())

        symbol_table_with_lines_transformer = SymbolTable({
            transform_to_uppercase.name: container(LinesTransformerConstant(transform_to_uppercase.value))
        })
        expected_symbol_references = asrt.matches_sequence([
            is_lines_transformer_reference_to(transform_to_uppercase.name)
        ])
        src_file_relativity = RelHomeOptionType.REL_HOME_ACT
        src_file_arg = PathArgumentWithRelativity('src-file.txt',
                                                  conf_rel_home(src_file_relativity))
        src_file = File(src_file_arg.file_name, src_file_contents)
        dst_file_relativity = RelOptionType.REL_ACT
        dst_file_arg = PathArgumentWithRelativity('dst-file.txt',
                                                  conf_rel_any(dst_file_relativity))
        expected_dst_dir_contents = DirContents([
            File(dst_file_arg.file_name, expected_dst_file_contents)
        ])
        instruction_argument = transform.ArgumentsConstructor(src_file_arg,
                                                              dst_file_arg,
                                                              transform_to_uppercase.name).construct()
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            # ACT & ASSERT #
            self.conf.run_test(
                self,
                source,
                arrangement=
                self.conf.arrangement(
                    hds_contents=home_populators.contents_in(src_file_relativity,
                                                             DirContents([
                                                                 src_file,
                                                             ])),
                    pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                    symbols=symbol_table_with_lines_transformer),
                expectation=
                self.conf.expect_success(
                    main_side_effects_on_sds=dir_contains_exactly(dst_file_relativity,
                                                                  expected_dst_dir_contents),
                    symbol_usages=expected_symbol_references,
                )
            )


class TestFailingValidationPreSds(TestCaseBase):
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


class TestFailingWhenDestinationFileExists(TestCaseBase):
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
