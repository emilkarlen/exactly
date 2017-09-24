import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelHomeOptionType
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
from exactly_lib_test.named_element.test_resources.lines_transformer import is_lines_transformer_reference_to
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.test_case_file_structure.test_resources import home_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import dir_contains_exactly
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_any, conf_rel_home
from exactly_lib_test.test_resources.file_structure import DirContents, File
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    test_cases = [
        TestCreateFileInExistingDirectory,
    ]
    suites = [tc(conf)
              for tc in test_cases]
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


class TestCreateFileInExistingDirectory(TestCaseBase):
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
