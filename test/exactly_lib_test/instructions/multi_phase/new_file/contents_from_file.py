import unittest
from typing import Sequence, Callable

from exactly_lib.instructions.multi_phase import new_file as sut
from exactly_lib.instructions.utils.parse import parse_file_maker
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType, RelOptionType, RelNonHdsOptionType
from exactly_lib.test_case_utils.string_transformer.impl.identity import IdentityStringTransformer
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.instructions.multi_phase.new_file.test_resources import utils as new_file_utils
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.arguments_building import \
    source_of, complete_argument_elements
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    TestCaseBase, \
    TestCommonFailingScenariosDueToInvalidDestinationFileBase, InvalidDestinationFileTestCasesData
from exactly_lib_test.instructions.multi_phase.new_file.test_resources.utils import Step, \
    ALLOWED_DST_FILE_RELATIVITIES, IS_FAILURE_OF_VALIDATION, IS_FAILURE, IS_SUCCESS, just_parse
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation, expectation
from exactly_lib_test.instructions.test_resources.parse_file_maker import file_with_rel_opt_conf, \
    accepted_non_hds_source_relativities, ALLOWED_SRC_FILE_RELATIVITIES, TransformableContentsConstructor
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_not_at_end
from exactly_lib_test.symbol.data.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.symbol.test_resources.string_transformer import is_reference_to_string_transformer__usage, \
    StringTransformerSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.string_transformers.test_resources.validation_cases import \
    failing_validation_cases
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_hds, every_conf_rel_hds, \
    conf_rel_non_hds, conf_rel_any, RelativityOptionConfigurationForRelNonHds, RelativityOptionConfiguration
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir, sym_link
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.string_transformer.test_resources.string_transformers import \
    MyToUppercaseTransformer


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

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            MyToUppercaseTransformer(),
        )

        src_file = fs.File('src-file.txt', 'contents of source file')
        src_file_symbol__str = NameAndValue('SRC_FILE_SYMBOL', src_file.name)
        src_file_rel_conf = conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)

        expected_dst_file = fs.File('dst-file-name.txt', src_file.contents.upper())

        dst_file_symbol = ConstantSuffixPathDdvSymbolContext(
            'DST_FILE_SYMBOL',
            RelOptionType.REL_TMP,
            expected_dst_file.name,
            sut.REL_OPT_ARG_CONF.options.accepted_relativity_variants,
        )

        file_contents_arg = TransformableContentsConstructor(
            file_with_rel_opt_conf(symbol_reference_syntax_for_name(src_file_symbol__str.name))
        ).with_transformation(to_upper_transformer.name).as_arguments

        # ACT & ASSERT #

        for phase_is_after_act in [False, True]:
            src_file_rel_opt_arg_conf = parse_file_maker._src_rel_opt_arg_conf_for_phase(phase_is_after_act)

            src_file_symbol = ConstantSuffixPathDdvSymbolContext(
                src_file_symbol__str.name,
                src_file_rel_conf.relativity_option,
                src_file_symbol__str.value,
                src_file_rel_opt_arg_conf.options.accepted_relativity_variants,
            )

            symbols = SymbolContext.symbol_table_of_contexts([
                src_file_symbol,
                dst_file_symbol,
                to_upper_transformer,
            ])

            source = remaining_source(
                '{file_name} {content_arguments}'.format(
                    file_name=dst_file_symbol.name__sym_ref_syntax,
                    content_arguments=file_contents_arg.first_line
                ),
                file_contents_arg.following_lines)

            with self.subTest(phase_is_after_act=phase_is_after_act):
                self._check(source,
                            ArrangementWithSds(
                                symbols=symbols,
                                hds_contents=src_file_rel_conf.populator_for_relativity_option_root__hds(
                                    DirContents([src_file]))
                            ),
                            Expectation(
                                main_result=IS_SUCCESS,
                                symbol_usages=asrt.matches_sequence([
                                    dst_file_symbol.reference_assertion__path_or_string,
                                    is_reference_to_string_transformer__usage(to_upper_transformer.name),
                                    src_file_symbol.reference_assertion__path_or_string,
                                ]),
                            ),
                            phase_is_after_act=phase_is_after_act
                            )

    def test_superfluous_arguments(self):
        # ARRANGE #

        arbitrary_transformer = 'TRANSFORMER_SYMBOL'

        src_file = PathArgumentWithRelativity('src-file.txt',
                                              conf_rel_hds(RelHdsOptionType.REL_HDS_CASE))

        file_contents_arguments_constructor = TransformableContentsConstructor(
            file_with_rel_opt_conf(src_file.file_name, src_file.relativity)
        )

        file_contents_cases = [
            NameAndValue(
                'contents of existing file / without transformation',
                file_contents_arguments_constructor.without_transformation()
            ),
            NameAndValue(
                'contents of existing file / with transformation',
                file_contents_arguments_constructor.with_transformation(arbitrary_transformer)
            ),
        ]

        for phase_is_after_act in [False, True]:
            for file_contents_case in file_contents_cases:
                optional_argument_elements = file_contents_case.value
                assert isinstance(optional_argument_elements, ArgumentElements)  # Type info for IDE
                optional_arguments = optional_argument_elements.as_arguments

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

    def test_validation_pre_sds_SHOULD_fail_WHEN_source_is_not_an_existing_file_rel_hds(self):
        self._check_of_invalid_src_file(lambda x: every_conf_rel_hds(),
                                        Step.VALIDATE_PRE_SDS)

    def test_main_SHOULD_fail_WHEN_source_is_not_an_existing_file_rel_non_hds(self):
        def every_src_file_rel_conf(is_before_act: bool) -> Sequence[RelativityOptionConfiguration]:
            return [
                conf_rel_non_hds(relativity)
                for relativity in accepted_non_hds_source_relativities(is_before_act)
            ]

        self._check_of_invalid_src_file(every_src_file_rel_conf, Step.MAIN)

    def test_all_relativities__without_transformer(self):
        # ARRANGE #

        src_file = fs.File('source-file.txt', 'contents of source file')
        expected_file = fs.File('a-file-name.txt', src_file.contents)

        for dst_rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            for src_rel_opt_conf in ALLOWED_SRC_FILE_RELATIVITIES:
                file_contents_arg = TransformableContentsConstructor(
                    file_with_rel_opt_conf(src_file.name, src_rel_opt_conf)
                ).without_transformation().as_arguments

                expected_non_hds_contents = self._expected_non_hds_contents(
                    dst_rel_opt_conf,
                    expected_file,
                    src_rel_opt_conf,
                    src_file)

                with self.subTest(dst_relativity=dst_rel_opt_conf.option_argument,
                                  src_relativity=src_rel_opt_conf.option_argument):
                    # ACT & ASSERT #

                    self._check(
                        remaining_source(
                            '{rel_opt} {file_name} {contents_arguments}'.format(
                                rel_opt=dst_rel_opt_conf.option_argument,
                                file_name=expected_file.file_name,
                                contents_arguments=file_contents_arg.first_line
                            ),
                            file_contents_arg.following_lines),
                        ArrangementWithSds(
                            pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                            tcds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                                DirContents([src_file]))
                        ),
                        Expectation(
                            main_result=IS_SUCCESS,
                            symbol_usages=asrt.is_empty_sequence,
                            main_side_effects_on_sds=expected_non_hds_contents,
                        ))

    def test_all_relativities__with_transformer(self):
        # ARRANGE #

        src_file = fs.File('source-file.txt', 'contents of source file')
        expected_file = fs.File('a-file-name.txt', src_file.contents.upper())

        to_upper_transformer = StringTransformerSymbolContext.of_primitive('TRANSFORMER_SYMBOL',
                                                                           MyToUppercaseTransformer())
        symbols = to_upper_transformer.symbol_table

        for dst_rel_opt_conf in ALLOWED_DST_FILE_RELATIVITIES:
            for src_rel_opt_conf in ALLOWED_SRC_FILE_RELATIVITIES:
                file_contents_arg = TransformableContentsConstructor(
                    file_with_rel_opt_conf(src_file.name, src_rel_opt_conf)
                ).with_transformation(to_upper_transformer.name).as_arguments
                expected_non_hds_contents = self._expected_non_hds_contents(
                    dst_rel_opt_conf,
                    expected_file,
                    src_rel_opt_conf,
                    src_file)

                with self.subTest(dst_option_string=dst_rel_opt_conf.option_argument,
                                  src_option_string=src_rel_opt_conf.option_argument):
                    # ACT & ASSERT #

                    self._check(
                        remaining_source(
                            '{rel_opt} {file_name} {contents_arguments}'.format(
                                rel_opt=dst_rel_opt_conf.option_argument,
                                file_name=expected_file.file_name,
                                contents_arguments=file_contents_arg.first_line
                            ),
                            file_contents_arg.following_lines),
                        ArrangementWithSds(
                            pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                            tcds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                                DirContents([src_file])),
                            symbols=symbols,
                        ),
                        Expectation(
                            main_result=IS_SUCCESS,
                            main_side_effects_on_sds=expected_non_hds_contents,
                            symbol_usages=asrt.matches_sequence([
                                is_reference_to_string_transformer__usage(to_upper_transformer.name),
                            ])
                        ))

    def test_validation_should_include_validation_of_string_transformer(self):
        # ARRANGE #

        src_file = fs.File('source-file.txt', 'contents of source file')
        expected_file = fs.File('a-file-name.txt', src_file.contents.upper())

        a_dst_rel_opt_conf = new_file_utils.AN_ALLOWED_DST_FILE_RELATIVITY
        a_src_rel_opt_conf = ALLOWED_SRC_FILE_RELATIVITIES[0]

        for failing_string_transformer_case in failing_validation_cases():
            failing_symbol_context = failing_string_transformer_case.value.symbol_context

            file_contents_arg = TransformableContentsConstructor(
                file_with_rel_opt_conf(src_file.name, a_src_rel_opt_conf)
            ).with_transformation(failing_symbol_context.name).as_arguments

            with self.subTest(failing_string_transformer_case.name):
                # ACT & ASSERT #

                self._check(
                    remaining_source(
                        '{rel_opt} {file_name} {contents_arguments_with_transformation}'.format(
                            rel_opt=a_dst_rel_opt_conf.option_argument,
                            file_name=expected_file.file_name,
                            contents_arguments_with_transformation=file_contents_arg.first_line
                        ),
                        file_contents_arg.following_lines),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                        tcds_contents=a_src_rel_opt_conf.populator_for_relativity_option_root(
                            DirContents([src_file])),
                        symbols=failing_symbol_context.symbol_table,
                    ),
                    expectation(
                        validation=failing_string_transformer_case.value.expectation,
                        symbol_usages=failing_symbol_context.references_assertion
                    ))

    def test_no_new_line_variants(self):
        # ARRANGE #

        identity_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            IdentityStringTransformer()
        )

        symbols = identity_transformer.symbol_table

        src_file = fs.File('src-file.txt', 'source file contents')
        src_file_rel_opt_conf = conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)

        expected_dst_file = fs.File('dst-file.txt', src_file.contents)
        dst_file_rel_opt_conf = conf_rel_non_hds(RelNonHdsOptionType.REL_ACT)

        file_arguments_constructor = TransformableContentsConstructor(
            file_with_rel_opt_conf(src_file.name,
                                   src_file_rel_opt_conf,
                                   with_new_line_after_source_type_option=True,
                                   ),
        )

        text_on_line_after_instruction = ' text on line after instruction'

        for with_file_maker_on_separate_line in [False, True]:
            file_contents_cases = [
                NameAndValue(
                    'without transformation',
                    file_arguments_constructor.without_transformation(
                        with_file_maker_on_separate_line=with_file_maker_on_separate_line)
                ),
                NameAndValue(
                    'with transformation',
                    file_arguments_constructor.with_transformation(
                        identity_transformer.name,
                        with_file_maker_on_separate_line=with_file_maker_on_separate_line)
                ),
            ]
            for file_contents_case in file_contents_cases:
                optional_arguments_elements = file_contents_case.value
                assert isinstance(optional_arguments_elements, ArgumentElements)  # Type info for IDE
                optional_arguments = optional_arguments_elements.as_arguments

                with self.subTest(file_contents_variant=file_contents_case.name,
                                  first_line_argments=optional_arguments.first_line,
                                  with_file_maker_on_separate_line=with_file_maker_on_separate_line):
                    source = remaining_source(
                        '{rel_opt} {dst_file_name} {optional_arguments}'.format(
                            rel_opt=dst_file_rel_opt_conf.option_argument,
                            dst_file_name=expected_dst_file.name,
                            optional_arguments=optional_arguments.first_line,
                        ),
                        optional_arguments.following_lines +
                        [text_on_line_after_instruction]
                    )

                    # ACT & ASSERT #

                    self._check(source,
                                ArrangementWithSds(
                                    pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                                    tcds_contents=src_file_rel_opt_conf.populator_for_relativity_option_root(
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

    def _check_of_invalid_src_file(
            self,
            is_after_act_2_every_src_file_rel_conf: Callable[[bool], Sequence[RelativityOptionConfiguration]],
            step_of_expected_failure: Step):
        # ARRANGE #
        transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            MyToUppercaseTransformer(),
        )
        symbols = transformer.symbol_table

        dst_file = PathArgumentWithRelativity('dst-file.txt',
                                              conf_rel_any(RelOptionType.REL_TMP))

        expectation = self._expect_failure_in(step_of_expected_failure)

        for phase_is_after_act in [False, True]:
            for src_file_rel_conf in is_after_act_2_every_src_file_rel_conf(phase_is_after_act):
                src_file = PathArgumentWithRelativity(self.src_file_name,
                                                      src_file_rel_conf)
                args_constructor = TransformableContentsConstructor(
                    file_with_rel_opt_conf(self.src_file_name, src_file_rel_conf)
                )
                for src_file_variant in self.src_file_variants:
                    for contents_arguments in args_constructor.with_and_without_transformer_cases(transformer.name):
                        arguments = complete_argument_elements(dst_file, contents_arguments).as_arguments
                        source = source_of(arguments)
                        with self.subTest(phase_is_after_act=phase_is_after_act,
                                          relativity_of_src_path=src_file.relativity.option_argument,
                                          first_line=arguments.first_line):
                            # ACT & ASSERT #
                            self._check(
                                source,
                                ArrangementWithSds(
                                    pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                                    tcds_contents=src_file.relativity.populator_for_relativity_option_root(
                                        src_file_variant.value),
                                    symbols=symbols,
                                ),
                                expectation,
                                phase_is_after_act=phase_is_after_act)

    @staticmethod
    def _expected_non_hds_contents(dst_file_rel_opt_conf: RelativityOptionConfigurationForRelNonHds,
                                   dst_file: fs.File,
                                   src_file_rel_opt_conf: RelativityOptionConfiguration,
                                   src_file: fs.File
                                   ) -> ValueAssertion:
        if dst_file_rel_opt_conf.option_argument_str == src_file_rel_opt_conf.option_string or \
                (dst_file_rel_opt_conf.is_rel_cwd and src_file_rel_opt_conf.is_rel_cwd):
            return dst_file_rel_opt_conf.assert_root_dir_contains_exactly(fs.DirContents([dst_file,
                                                                                          src_file]))
        else:
            return dst_file_rel_opt_conf.assert_root_dir_contains_exactly(fs.DirContents([dst_file]))


class TestCommonFailingScenariosDueToInvalidDestinationFile(TestCommonFailingScenariosDueToInvalidDestinationFileBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        arbitrary_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            MyToUppercaseTransformer(),
        )

        symbols = arbitrary_transformer.symbol_table

        src_file = PathArgumentWithRelativity('src-file.txt',
                                              conf_rel_hds(RelHdsOptionType.REL_HDS_CASE))

        file_contents_arguments_constructor = TransformableContentsConstructor(
            file_with_rel_opt_conf(src_file.file_name, src_file.relativity)
        )

        src_file_in_hds_contents = src_file.relativity.populator_for_relativity_option_root(
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
            src_file_in_hds_contents)
