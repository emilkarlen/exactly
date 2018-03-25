import types
import unittest

from exactly_lib.instructions.multi_phase_instructions import new_file as sut
from exactly_lib.instructions.utils.parse import parse_file_maker
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.data.file_ref_resolver_impls.file_ref_resolvers import resolver_of_rel_option
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType, RelOptionType, RelNonHomeOptionType
from exactly_lib.test_case_utils.lines_transformer.transformers import IdentityLinesTransformer
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase_instructions.new_file.test_resources import TestCaseBase, \
    IS_SUCCESS, just_parse, Step, \
    ALLOWED_DST_FILE_RELATIVITIES, IS_FAILURE_OF_VALIDATION, IS_FAILURE, complete_arguments, source_of, \
    TestCommonFailingScenariosDueToInvalidDestinationFileBase, InvalidDestinationFileTestCasesData
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.utils.parse.parse_file_maker.test_resources.arguments import file, \
    accepted_non_home_source_relativities, ALLOWED_SRC_FILE_RELATIVITIES, TransformableContentsConstructor
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_not_at_end
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_reference
from exactly_lib_test.symbol.test_resources.lines_transformer import LinesTransformerResolverConstantTestImpl, \
    is_lines_transformer_reference_to
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.test_transformers import \
    MyToUppercaseTransformer
from exactly_lib_test.test_case_utils.parse.parse_file_ref import file_ref_or_string_reference_restrictions
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_home, every_conf_rel_home, \
    conf_rel_non_home, conf_rel_any, RelativityOptionConfigurationForRelNonHome, RelativityOptionConfiguration
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, sym_link
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestScenariosWithContentsFromFile),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
    ])


class TestScenariosWithContentsFromFile(TestCaseBase):
    src_file_name = 'src-file.txt'

    src_file_variants = [
        NameAndValue('no file',
                     DirContents([])),
        NameAndValue('file is a directory',
                     DirContents([empty_dir(src_file_name)])),
        NameAndValue('file is a broken symlink',
                     DirContents([sym_link(src_file_name, 'non-existing-target-file')])),

    ]

    def test_symbol_usages(self):
        # ARRANGE #

        to_upper_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))

        src_file = fs.File('src-file.txt', 'contents of source file')
        src_file_symbol = NameAndValue('SRC_FILE_SYMBOL', src_file.name)
        src_file_rel_conf = conf_rel_home(RelHomeOptionType.REL_HOME_CASE)

        expected_dst_file = fs.File('dst-file-name.txt', src_file.contents.upper())
        dst_file_symbol = NameAndValue('DST_FILE_SYMBOL', expected_dst_file.name)
        dst_file_rel_option = RelOptionType.REL_TMP

        file_contents_arg = TransformableContentsConstructor(
            file(symbol_reference_syntax_for_name(src_file_symbol.name))
        ).with_transformation(to_upper_transformer.name)

        symbols = SymbolTable({
            src_file_symbol.name:
                container(resolver_of_rel_option(src_file_rel_conf.relativity_option,
                                                 PathPartAsFixedPath(src_file_symbol.value))),

            dst_file_symbol.name:
                container(resolver_of_rel_option(dst_file_rel_option,
                                                 PathPartAsFixedPath(dst_file_symbol.value))),

            to_upper_transformer.name:
                container(to_upper_transformer.value),
        })

        # ACT & ASSERT #

        for phase_is_after_act in [False, True]:
            src_file_rel_opt_arg_conf = parse_file_maker._src_rel_opt_arg_conf_for_phase(phase_is_after_act)

            source = remaining_source(
                '{file_name} {content_arguments}'.format(
                    file_name=symbol_reference_syntax_for_name(dst_file_symbol.name),
                    content_arguments=file_contents_arg.first_line
                ),
                file_contents_arg.following_lines)

            with self.subTest(phase_is_after_act=phase_is_after_act):
                self._check(source,
                            ArrangementWithSds(
                                symbols=symbols,
                                hds_contents=src_file_rel_conf.populator_for_relativity_option_root__home(
                                    DirContents([src_file]))
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

                                    equals_symbol_reference(
                                        SymbolReference(src_file_symbol.name,
                                                        file_ref_or_string_reference_restrictions(
                                                            src_file_rel_opt_arg_conf.options.accepted_relativity_variants))
                                    ),
                                ]),
                            ),
                            phase_is_after_act=phase_is_after_act
                            )

    def test_superfluous_arguments(self):
        # ARRANGE #

        arbitrary_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                             LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))

        src_file = PathArgumentWithRelativity('src-file.txt',
                                              conf_rel_home(RelHomeOptionType.REL_HOME_CASE))

        file_contents_arguments_constructor = TransformableContentsConstructor(
            file(src_file.file_name, src_file.relativity)
        )

        file_contents_cases = [
            NameAndValue(
                'contents of existing file / without transformation',
                file_contents_arguments_constructor.without_transformation()
            ),
            NameAndValue(
                'contents of existing file / with transformation',
                file_contents_arguments_constructor.with_transformation(arbitrary_transformer.name)
            ),
        ]

        for phase_is_after_act in [False, True]:
            for file_contents_case in file_contents_cases:
                optional_arguments = file_contents_case.value
                assert isinstance(optional_arguments, Arguments)  # Type info for IDE

                with self.subTest(phase_is_after_act=phase_is_after_act,
                                  file_contents_variant=file_contents_case.name,
                                  first_line_argments=optional_arguments.first_line):
                    source = remaining_source(
                        '{dst_file_argument} {contents_arguments} superfluous_arg'.format(
                            dst_file_argument='dst-file.txt',
                            contents_arguments=optional_arguments.first_line,
                        ),
                        optional_arguments.following_lines)

                    # ACT & ASSERT #
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        just_parse(source,
                                   phase_is_after_act=phase_is_after_act)

    def test_validation_pre_sds_SHOULD_fail_WHEN_source_is_not_an_existing_file_rel_home(self):
        self._check_of_invalid_src_file(lambda x: every_conf_rel_home(),
                                        Step.VALIDATE_PRE_SDS)

    def test_main_SHOULD_fail_WHEN_source_is_not_an_existing_file_rel_non_home(self):
        def every_src_file_rel_conf(is_before_act: bool):
            return [
                conf_rel_non_home(relativity)
                for relativity in accepted_non_home_source_relativities(is_before_act)
            ]

        self._check_of_invalid_src_file(every_src_file_rel_conf, Step.MAIN)

    def test_all_relativities__without_transformer(self):
        # ARRANGE #

        src_file = fs.File('source-file.txt', 'contents of source file')
        expected_file = fs.File('a-file-name.txt', src_file.contents)

        for dst_rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            for src_rel_opt_conf in ALLOWED_SRC_FILE_RELATIVITIES:
                file_contents_arg = TransformableContentsConstructor(
                    file(src_file.name, src_rel_opt_conf)
                ).without_transformation()

                expected_non_home_contents = self._expected_non_home_contents(
                    dst_rel_opt_conf,
                    expected_file,
                    src_rel_opt_conf,
                    src_file)

                with self.subTest(dst_relativity=dst_rel_opt_conf.option_string,
                                  src_relativity=src_rel_opt_conf.option_string):
                    # ACT & ASSERT #

                    self._check(
                        remaining_source(
                            '{rel_opt} {file_name} {contents_arguments}'.format(
                                rel_opt=dst_rel_opt_conf.option_string,
                                file_name=expected_file.file_name,
                                contents_arguments=file_contents_arg.first_line
                            ),
                            file_contents_arg.following_lines),
                        ArrangementWithSds(
                            pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                            home_or_sds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                                DirContents([src_file]))
                        ),
                        Expectation(
                            main_result=IS_SUCCESS,
                            symbol_usages=asrt.is_empty_sequence,
                            main_side_effects_on_sds=expected_non_home_contents,
                        ))

    def test_all_relativities__with_transformer(self):
        # ARRANGE #

        src_file = fs.File('source-file.txt', 'contents of source file')
        expected_file = fs.File('a-file-name.txt', src_file.contents.upper())

        to_upper_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        symbols = SymbolTable({
            to_upper_transformer.name:
                container(to_upper_transformer.value),
        })

        for dst_rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            for src_rel_opt_conf in ALLOWED_SRC_FILE_RELATIVITIES:
                file_contents_arg = TransformableContentsConstructor(
                    file(src_file.name, src_rel_opt_conf)
                ).with_transformation(to_upper_transformer.name)

                expected_non_home_contents = self._expected_non_home_contents(
                    dst_rel_opt_conf,
                    expected_file,
                    src_rel_opt_conf,
                    src_file)

                with self.subTest(dst_option_string=dst_rel_opt_conf.option_string,
                                  src_option_string=src_rel_opt_conf.option_string):
                    # ACT & ASSERT #

                    self._check(
                        remaining_source(
                            '{rel_opt} {file_name} {contents_arguments}'.format(
                                rel_opt=dst_rel_opt_conf.option_string,
                                file_name=expected_file.file_name,
                                contents_arguments=file_contents_arg.first_line
                            ),
                            file_contents_arg.following_lines),
                        ArrangementWithSds(
                            pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                            home_or_sds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                                DirContents([src_file])),
                            symbols=symbols,
                        ),
                        Expectation(
                            main_result=IS_SUCCESS,
                            main_side_effects_on_sds=expected_non_home_contents,
                            symbol_usages=asrt.matches_sequence([
                                is_lines_transformer_reference_to(to_upper_transformer.name),
                            ])
                        ))

    def test_new_line_before_mandatory_arguments_SHOULD_be_accepted(self):
        # ARRANGE #

        identity_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            LinesTransformerResolverConstantTestImpl(IdentityLinesTransformer()))

        symbols = SymbolTable({
            identity_transformer.name: container(identity_transformer.value),
        })

        src_file = fs.File('src-file.txt', 'source file contents')
        src_file_rel_opt_conf = conf_rel_home(RelHomeOptionType.REL_HOME_CASE)

        expected_dst_file = fs.File('dst-file.txt', src_file.contents)
        dst_file_rel_opt_conf = conf_rel_non_home(RelNonHomeOptionType.REL_ACT)

        file_arguments_constructor = TransformableContentsConstructor(
            file(src_file.name,
                 src_file_rel_opt_conf,
                 with_new_line_after_output_option=True,
                 ),
            with_new_line_after_transformer=True,
        )

        file_contents_cases = [
            NameAndValue(
                'without transformation',
                file_arguments_constructor.without_transformation()
            ),
            NameAndValue(
                'with transformation',
                file_arguments_constructor.with_transformation(identity_transformer.name)
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
                                home_or_sds_contents=src_file_rel_opt_conf.populator_for_relativity_option_root(
                                    DirContents([src_file])),
                                symbols=symbols,
                            ),
                            Expectation(
                                main_result=IS_SUCCESS,
                                symbol_usages=asrt.anything_goes(),
                                main_side_effects_on_sds=dst_file_rel_opt_conf.assert_root_dir_contains_exactly(
                                    fs.DirContents([expected_dst_file])),
                                source=source_is_not_at_end(
                                    remaining_part_of_current_line=asrt.equals(text_on_line_after_instruction)
                                )
                            )
                            )

    @staticmethod
    def _expect_failure_in(step_of_expected_failure: Step) -> Expectation:
        symbol_usages_expectation = asrt.is_sequence_of(asrt.is_instance(SymbolReference))

        if step_of_expected_failure is Step.VALIDATE_PRE_SDS:
            return Expectation(validation_pre_sds=IS_FAILURE_OF_VALIDATION,
                               symbol_usages=symbol_usages_expectation)
        else:
            return Expectation(main_result=IS_FAILURE,
                               symbol_usages=symbol_usages_expectation)

    def _check_of_invalid_src_file(self,
                                   is_after_act_2_every_src_file_rel_conf: types.FunctionType,
                                   step_of_expected_failure: Step):
        # ARRANGE #
        transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                   LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        symbols = SymbolTable({
            transformer.name:
                container(transformer.value),
        })

        dst_file = PathArgumentWithRelativity('dst-file.txt',
                                              conf_rel_any(RelOptionType.REL_TMP))

        expectation = self._expect_failure_in(step_of_expected_failure)

        for phase_is_after_act in [False, True]:
            for src_file_rel_conf in is_after_act_2_every_src_file_rel_conf(phase_is_after_act):
                src_file = PathArgumentWithRelativity(self.src_file_name,
                                                      src_file_rel_conf)
                args_constructor = TransformableContentsConstructor(
                    file(self.src_file_name, src_file_rel_conf)
                )
                for src_file_variant in self.src_file_variants:
                    for contents_arguments in args_constructor.with_and_without_transformer_cases(transformer.name):
                        arguments = complete_arguments(dst_file, contents_arguments)
                        source = source_of(arguments)
                        with self.subTest(phase_is_after_act=phase_is_after_act,
                                          relativity_of_src_path=src_file.relativity.option_string,
                                          first_line=arguments.first_line):
                            # ACT & ASSERT #
                            self._check(
                                source,
                                ArrangementWithSds(
                                    pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                                    home_or_sds_contents=src_file.relativity.populator_for_relativity_option_root(
                                        src_file_variant.value),
                                    symbols=symbols,
                                ),
                                expectation,
                                phase_is_after_act=phase_is_after_act)

    @staticmethod
    def _expected_non_home_contents(dst_file_rel_opt_conf: RelativityOptionConfigurationForRelNonHome,
                                    dst_file: fs.File,
                                    src_file_rel_opt_conf: RelativityOptionConfiguration,
                                    src_file: fs.File
                                    ) -> asrt.ValueAssertion:
        if dst_file_rel_opt_conf.option_string == src_file_rel_opt_conf.option_string or \
                (dst_file_rel_opt_conf.is_rel_cwd and src_file_rel_opt_conf.is_rel_cwd):
            return dst_file_rel_opt_conf.assert_root_dir_contains_exactly(fs.DirContents([dst_file,
                                                                                          src_file]))
        else:
            return dst_file_rel_opt_conf.assert_root_dir_contains_exactly(fs.DirContents([dst_file]))


class TestCommonFailingScenariosDueToInvalidDestinationFile(TestCommonFailingScenariosDueToInvalidDestinationFileBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        arbitrary_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                             LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))

        symbols = SymbolTable({
            arbitrary_transformer.name: container(arbitrary_transformer.value),
        })

        src_file = PathArgumentWithRelativity('src-file.txt',
                                              conf_rel_home(RelHomeOptionType.REL_HOME_CASE))

        file_contents_arguments_constructor = TransformableContentsConstructor(
            file(src_file.file_name, src_file.relativity)
        )

        src_file_in_home_contents = src_file.relativity.populator_for_relativity_option_root(
            DirContents([fs.empty_file(src_file.file_name)])
        )

        file_contents_cases = [
            NameAndValue(
                'contents of existing file / without transformation',
                file_contents_arguments_constructor.without_transformation()
            ),
            NameAndValue(
                'contents of existing file / with transformation',
                file_contents_arguments_constructor.with_transformation(arbitrary_transformer.name)
            ),
        ]

        return InvalidDestinationFileTestCasesData(
            file_contents_cases,
            symbols,
            src_file_in_home_contents)
