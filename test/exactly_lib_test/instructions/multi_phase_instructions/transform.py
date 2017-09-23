import unittest

from exactly_lib.instructions.multi_phase_instructions import transform as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType, RelOptionType, RelNonHomeOptionType, \
    PathRelativityVariants, RelSdsOptionType
from exactly_lib.test_case_utils.lines_transformer.resolvers import LinesTransformerConstant
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources.file_contents.contents_transformation import \
    ToUppercaseLinesTransformer
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation, \
    ArrangementWithSds, check
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.named_element.symbol.restrictions.test_resources.concrete_restriction_assertion import \
    equals_symbol_reference_restrictions
from exactly_lib_test.named_element.test_resources.lines_transformer import is_lines_transformer_reference_to
from exactly_lib_test.named_element.test_resources.named_elem_utils import container
from exactly_lib_test.named_element.test_resources.resolver_structure_assertions import matches_reference
from exactly_lib_test.named_element.test_resources.symbol_syntax import A_VALID_SYMBOL_NAME
from exactly_lib_test.named_element.test_resources.symbol_tables import singleton_symbol_table_3
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import dir_contains_exactly
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.argument_syntax import \
    syntax_for_arbitrary_lines_transformer_without_symbol_references
from exactly_lib_test.test_case_utils.parse.parse_file_ref import file_ref_reference_restrictions
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_home, conf_rel_any, \
    conf_rel_non_home, symbol_conf_rel_home, symbol_conf_rel_sds
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, sym_link, File
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.values import FakeLinesTransformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestFailingScenarios),
        unittest.makeSuite(TestSymbolUsages),
        unittest.makeSuite(TestConsumptionOfSource),
        unittest.makeSuite(TestSuccessfulScenarios),
    ])


class TestFailingParse(unittest.TestCase):
    def test_parse_SHOULD_fail_WHEN_arguments_are_invalid(self):
        cases = [
            '',
            'file1',
            'file1 file2 transformer superfluous',
        ]
        parser = sut.EmbryoParser()
        for argument_str in cases:
            source = remaining_source(argument_str)
            with self.subTest(argument_str=argument_str):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(source)


class TestFailingScenarios(unittest.TestCase):
    src_file_name = 'src-file'
    source_file_variants = [
        NameAndValue('no file',
                     DirContents([])),
        NameAndValue('file is a directory',
                     DirContents([empty_dir(src_file_name)])),
        NameAndValue('file is a broken symlink',
                     DirContents([sym_link(src_file_name, 'non-existing-target-file')])),

    ]

    def test_validation_pre_sds_SHOULD_fail_WHEN_source_is_not_an_existing_file_rel_home(self):
        name_of_transformer_symbol = A_VALID_SYMBOL_NAME
        transformer_argument_variants = [
            '',
            name_of_transformer_symbol,
        ]
        symbols = singleton_symbol_table_3(name_of_transformer_symbol,
                                           LinesTransformerConstant(
                                               FakeLinesTransformer()))
        dst_file = PathArgumentWithRelativity('dst-file',
                                              conf_rel_any(RelOptionType.REL_TMP))
        for rel_home_relativity in RelHomeOptionType:
            src_file = PathArgumentWithRelativity(self.src_file_name,
                                                  conf_rel_home(rel_home_relativity))
            for source_file_variant in self.source_file_variants:
                for transformer in transformer_argument_variants:
                    source = remaining_source(ArgumentsConstructor(src_file, dst_file).construct())
                    with self.subTest(relativity_of_src_path=src_file.relativity.option_string,
                                      transformer=transformer,
                                      source_file_variant=source_file_variant.name):
                        check(self,
                              sut.EmbryoParser(),
                              source,
                              ArrangementWithSds(
                                  pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                                  home_or_sds_contents=src_file.relativity.populator_for_relativity_option_root(
                                      source_file_variant.value),
                                  symbols=symbols,
                              ),
                              Expectation(
                                  validation_pre_sds=IS_FAILURE_OF_VALIDATION,
                                  symbol_usages=asrt.anything_goes(),
                              ))

    def test_main_result_SHOULD_be_failure_WHEN_source_is_not_an_existing_file_rel_non_home(self):
        name_of_transformer_symbol = A_VALID_SYMBOL_NAME
        transformer_argument_variants = [
            '',
            name_of_transformer_symbol,
        ]
        symbols = singleton_symbol_table_3(name_of_transformer_symbol,
                                           LinesTransformerConstant(
                                               FakeLinesTransformer()))
        dst_file = PathArgumentWithRelativity('dst-file',
                                              conf_rel_any(RelOptionType.REL_TMP))
        for rel_non_home_relativity in RelNonHomeOptionType:
            src_file = PathArgumentWithRelativity('src-file',
                                                  conf_rel_non_home(rel_non_home_relativity))
            for transformer in transformer_argument_variants:
                for source_file_variant in self.source_file_variants:
                    source = remaining_source(ArgumentsConstructor(src_file, dst_file).construct())
                    with self.subTest(relativity_of_src_path=src_file.relativity.option_string,
                                      transformer=transformer,
                                      source_file_variant=source_file_variant.name):
                        check(self,
                              sut.EmbryoParser(),
                              source,
                              ArrangementWithSds(
                                  pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                                  home_or_sds_contents=src_file.relativity.populator_for_relativity_option_root(
                                      source_file_variant.value),
                                  symbols=symbols,
                              ),
                              Expectation(
                                  main_result=IS_FAILURE_OF_MAIN,
                                  symbol_usages=asrt.anything_goes(),
                              ))

    def test_main_result_SHOULD_be_failure_WHEN_destination_file_exists(self):
        name_of_transformer_symbol = A_VALID_SYMBOL_NAME
        transformer_argument_variants = [
            '',
            name_of_transformer_symbol,
        ]
        symbols = singleton_symbol_table_3(name_of_transformer_symbol,
                                           LinesTransformerConstant(
                                               FakeLinesTransformer()))
        src_file_arg = PathArgumentWithRelativity('src-file',
                                                  conf_rel_home(RelHomeOptionType.REL_HOME_CASE))

        dst_file_arg = PathArgumentWithRelativity('dst-file',
                                                  conf_rel_any(RelOptionType.REL_TMP))
        dst_file_variants = [
            empty_file(dst_file_arg.file_name),
            empty_dir(dst_file_arg.file_name),
            sym_link(dst_file_arg.file_name, 'non-existing-target'),
        ]
        for dst_file in dst_file_variants:
            for transformer in transformer_argument_variants:
                source = remaining_source(ArgumentsConstructor(src_file_arg, dst_file_arg).construct())
                with self.subTest(relativity_of_src_path=src_file_arg.relativity.option_string,
                                  transformer=transformer,
                                  dst_file=str(type(dst_file))):
                    check(self,
                          sut.EmbryoParser(),
                          source,
                          ArrangementWithSds(
                              pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                              home_or_sds_contents=home_and_sds_populators.multiple([
                                  src_file_arg.relativity.populator_for_relativity_option_root(
                                      DirContents([
                                          empty_file(src_file_arg.file_name)
                                      ])),
                                  dst_file_arg.relativity.populator_for_relativity_option_root(
                                      DirContents([
                                          dst_file
                                      ]))]),
                              symbols=symbols,
                          ),
                          Expectation(
                              main_result=IS_FAILURE_OF_MAIN,
                              symbol_usages=asrt.anything_goes(),
                          ))


class TestSymbolUsages(unittest.TestCase):
    def test_symbols_in_src_file_SHOULD_be_reported(self):
        # ARRANGE #
        line_transformer_variants = [
            '',
            syntax_for_arbitrary_lines_transformer_without_symbol_references(),
        ]
        symbol_name = 'path_symbol'
        src_file_arg = PathArgumentWithRelativity('src-file',
                                                  symbol_conf_rel_home(RelHomeOptionType.REL_HOME_CASE,
                                                                       symbol_name,
                                                                       SRC_PATH_RELATIVITY_VARIANTS))

        dst_file_arg = PathArgumentWithRelativity('dst-file',
                                                  conf_rel_any(RelOptionType.REL_TMP))
        for line_transformer in line_transformer_variants:
            with self.subTest(line_transformer=line_transformer):
                source = remaining_source(ArgumentsConstructor(src_file_arg,
                                                               dst_file_arg,
                                                               line_transformer).construct())
                # ACT #
                instruction = sut.EmbryoParser().parse(source)
                # ASSERT #
                expected_symbol_references = asrt.matches_sequence([
                    matches_reference(asrt.equals(symbol_name),
                                      equals_symbol_reference_restrictions(
                                          file_ref_reference_restrictions(SRC_PATH_RELATIVITY_VARIANTS)))
                ])
                expected_symbol_references.apply_without_message(self,
                                                                 instruction.symbol_usages)

    def test_symbols_in_dst_file_SHOULD_be_reported(self):
        # ARRANGE #
        line_transformer_variants = [
            '',
            syntax_for_arbitrary_lines_transformer_without_symbol_references(),
        ]
        symbol_name = 'path_symbol'
        src_file_arg = PathArgumentWithRelativity('src-file',
                                                  conf_rel_any(RelOptionType.REL_TMP))

        dst_file_arg = PathArgumentWithRelativity('dst-file',
                                                  symbol_conf_rel_sds(RelSdsOptionType.REL_TMP,
                                                                      symbol_name,
                                                                      DST_PATH_RELATIVITY_VARIANTS))
        for line_transformer in line_transformer_variants:
            with self.subTest(line_transformer=line_transformer):
                source = remaining_source(ArgumentsConstructor(src_file_arg,
                                                               dst_file_arg,
                                                               line_transformer).construct())
                # ACT #
                instruction = sut.EmbryoParser().parse(source)
                # ASSERT #
                expected_symbol_references = asrt.matches_sequence([
                    matches_reference(asrt.equals(symbol_name),
                                      equals_symbol_reference_restrictions(
                                          file_ref_reference_restrictions(DST_PATH_RELATIVITY_VARIANTS)))
                ])
                expected_symbol_references.apply_without_message(self,
                                                                 instruction.symbol_usages)

    def test_symbols_in_transformer_SHOULD_be_reported(self):
        # ARRANGE #
        symbol_name = 'transformer_symbol'
        src_file_arg = PathArgumentWithRelativity('src-file',
                                                  conf_rel_any(RelOptionType.REL_TMP))

        dst_file_arg = PathArgumentWithRelativity('dst-file',
                                                  conf_rel_any(RelOptionType.REL_TMP))
        source = remaining_source(ArgumentsConstructor(src_file_arg,
                                                       dst_file_arg,
                                                       symbol_name).construct())
        # ACT #
        instruction = sut.EmbryoParser().parse(source)
        # ASSERT #
        expected_symbol_references = asrt.matches_sequence([
            is_lines_transformer_reference_to(symbol_name)])
        expected_symbol_references.apply_without_message(self,
                                                         instruction.symbol_usages)


class TestConsumptionOfSource(unittest.TestCase):
    def test_sans_transformer(self):
        # ARRANGE #
        parser = sut.EmbryoParser()
        src_file_arg = PathArgumentWithRelativity('src-file',
                                                  conf_rel_any(RelOptionType.REL_TMP))

        dst_file_arg = PathArgumentWithRelativity('dst-file',
                                                  conf_rel_any(RelOptionType.REL_TMP))
        argument_str = ArgumentsConstructor(src_file_arg, dst_file_arg).construct()
        for source in equivalent_source_variants__with_source_check(self, argument_str):
            with self.subTest(source=source.remaining_source):
                # ACT & ASSERT #
                parser.parse(source)

    def test_with_transformer(self):
        # ARRANGE #
        parser = sut.EmbryoParser()
        src_file_arg = PathArgumentWithRelativity('src-file',
                                                  conf_rel_any(RelOptionType.REL_TMP))

        dst_file_arg = PathArgumentWithRelativity('dst-file',
                                                  conf_rel_any(RelOptionType.REL_TMP))
        argument_str = ArgumentsConstructor(
            src_file_arg,
            dst_file_arg,
            syntax_for_arbitrary_lines_transformer_without_symbol_references()).construct()
        for source in equivalent_source_variants__with_source_check(self, argument_str):
            with self.subTest(source=source.remaining_source):
                # ACT & ASSERT #
                parser.parse(source)


class TestSuccessfulScenarios(unittest.TestCase):
    def _check(self,
               source_file_contents: str,
               expected_destination_file_contents: str,
               transformer_argument: str,
               expected_symbol_references: asrt.ValueAssertion,
               symbols: SymbolTable = None,
               ):
        for src_file_relativity in SRC_PATH_RELATIVITY_VARIANTS.rel_option_types:
            src_file_arg = PathArgumentWithRelativity('src-file.txt',
                                                      conf_rel_any(src_file_relativity))
            src_file = File(src_file_arg.file_name, source_file_contents)
            for dst_file_relativity in DST_PATH_RELATIVITY_VARIANTS.rel_option_types:
                dst_file_arg = PathArgumentWithRelativity('dst-file.txt',
                                                          conf_rel_any(dst_file_relativity))
                expected_files_in_dst_dir = [
                    File(dst_file_arg.file_name, expected_destination_file_contents)
                ]
                if dst_file_relativity == src_file_relativity:
                    expected_files_in_dst_dir.append(src_file)
                expected_dst_dir_contents = DirContents(expected_files_in_dst_dir)
                source = remaining_source(ArgumentsConstructor(src_file_arg,
                                                               dst_file_arg,
                                                               transformer_argument).construct())
                with self.subTest(relativity_of_src_path=src_file_arg.relativity.option_string,
                                  src_file=src_file_relativity.name,
                                  dst_file=dst_file_relativity.name,
                                  ):
                    check(self,
                          sut.EmbryoParser(),
                          source,
                          ArrangementWithSds(
                              pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                              home_or_sds_contents=src_file_arg.relativity.populator_for_relativity_option_root(
                                  DirContents([
                                      src_file,
                                  ])),
                              symbols=symbols,
                          ),
                          Expectation(
                              main_result=IS_SUCCESS_OF_MAIN,
                              main_side_effects_on_sds=dir_contains_exactly(dst_file_relativity,
                                                                            expected_dst_dir_contents),
                              symbol_usages=expected_symbol_references,
                          ))

    def test_sans_transformer(self):
        file_contents = 'source file contents'
        self._check(
            source_file_contents=file_contents,
            expected_destination_file_contents=file_contents,
            transformer_argument='',
            expected_symbol_references=asrt.is_empty_list,
        )

    def test_with_transformer(self):
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

        self._check(
            source_file_contents=src_file_contents,
            expected_destination_file_contents=expected_dst_file_contents,
            transformer_argument=transform_to_uppercase.name,
            symbols=symbol_table_with_lines_transformer,
            expected_symbol_references=expected_symbol_references,
        )


class ArgumentsConstructor:
    def __init__(self,
                 src_file: PathArgumentWithRelativity,
                 dst_file: PathArgumentWithRelativity,
                 transformer: str = ''
                 ):
        self._src_file = src_file
        self._dst_file = dst_file
        self._transformer = transformer

    @property
    def src_file(self) -> PathArgumentWithRelativity:
        return self._src_file

    @property
    def dst_file(self) -> PathArgumentWithRelativity:
        return self._dst_file

    def construct(self) -> str:
        return '{src} {dst} {transformer}'.format(
            src=self._src_file.argument_str,
            dst=self._dst_file.argument_str,
            transformer=self._transformer
        )


IS_FAILURE_OF_VALIDATION = asrt.is_instance(str)

IS_FAILURE_OF_MAIN = asrt.is_instance(str)
IS_SUCCESS_OF_MAIN = asrt.is_none

SRC_PATH_RELATIVITY_VARIANTS = PathRelativityVariants(
    {
        RelOptionType.REL_CWD,
        RelOptionType.REL_HOME_CASE,
        RelOptionType.REL_HOME_ACT,
        RelOptionType.REL_ACT,
        RelOptionType.REL_TMP,
        RelOptionType.REL_RESULT,
    },
    True)

DST_PATH_RELATIVITY_VARIANTS = PathRelativityVariants(
    {
        RelOptionType.REL_CWD,
        RelOptionType.REL_ACT,
        RelOptionType.REL_TMP,
    },
    False)
