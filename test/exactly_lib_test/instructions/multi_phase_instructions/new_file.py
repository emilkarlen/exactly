import types
import unittest
from enum import Enum

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.multi_phase_instructions import new_file as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.data.string_resolver import string_constant
from exactly_lib.symbol.data.value_resolvers.file_ref_resolvers import resolver_of_rel_option
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelNonHomeOptionType, \
    PathRelativityVariants, RelHomeOptionType, RelSdsOptionType
from exactly_lib.test_case_utils.parse import parse_file_ref
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.section_document.test_resources.parse_source import single_line_source, remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import source_is_at_end, \
    is_at_beginning_of_line
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    equals_data_type_reference_restrictions
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references, \
    equals_symbol_reference
from exactly_lib_test.symbol.test_resources.lines_transformer import LinesTransformerResolverConstantTestImpl, \
    is_lines_transformer_reference_to
from exactly_lib_test.symbol.test_resources.resolver_structure_assertions import matches_reference_2
from exactly_lib_test.symbol.test_resources.symbol_utils import container
from exactly_lib_test.test_case_file_structure.test_resources.sds_check.sds_contents_check import \
    non_home_dir_contains_exactly, dir_contains_exactly
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.test_transformers import \
    MyToUppercaseTransformer
from exactly_lib_test.test_case_utils.parse.parse_file_ref import file_ref_or_string_reference_restrictions
from exactly_lib_test.test_case_utils.parse.test_resources.relativity_arguments import args_with_rel_ops
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_any, \
    conf_rel_non_home, default_conf_rel_non_home, conf_rel_home, conf_rel_sds, RelativityOptionConfiguration, \
    every_conf_rel_home
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, Dir, empty_dir, sym_link
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.programs.shell_commands import command_that_prints_line_to_stdout
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParseWithNoContents),
        unittest.makeSuite(TestFailingParseWithContents),

        unittest.makeSuite(TestSuccessfulScenariosWithNoContents),
        unittest.makeSuite(TestSuccessfulScenariosWithConstantContents),
        unittest.makeSuite(TestScenariosWithContentsFromFile),
        unittest.makeSuite(TestScenariosWithContentsFromProcessOutput),

        unittest.makeSuite(TestParserConsumptionOfSource),
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),

        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name', False)),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name', True)),
    ])


def is_success() -> asrt.ValueAssertion:
    return asrt.is_none


def is_failure() -> asrt.ValueAssertion:
    return asrt.is_instance(str)


class Step(Enum):
    VALIDATE_PRE_SDS = 1
    MAIN = 2


DISALLOWED_RELATIVITIES = [
    RelOptionType.REL_RESULT,
    RelOptionType.REL_HOME_CASE,
    RelOptionType.REL_HOME_ACT,
]

ALLOWED_SOURCE_FILE_RELATIVITIES = [
    conf_rel_home(RelHomeOptionType.REL_HOME_CASE),
    conf_rel_home(RelHomeOptionType.REL_HOME_ACT),
    conf_rel_sds(RelSdsOptionType.REL_ACT),
    conf_rel_sds(RelSdsOptionType.REL_TMP),
    conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
]

ALLOWED_RELATIVITIES = [
    conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
    conf_rel_non_home(RelNonHomeOptionType.REL_TMP),
    conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
    default_conf_rel_non_home(RelNonHomeOptionType.REL_CWD),

]

ACCEPTED_RELATIVITY_VARIANTS = PathRelativityVariants({RelOptionType.REL_ACT,
                                                       RelOptionType.REL_TMP,
                                                       RelOptionType.REL_CWD},
                                                      absolute=False)


class TestFailingParseWithNoContents(unittest.TestCase):
    def test_path_is_mandatory__without_option(self):
        arguments = ''
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _just_parse(single_line_source(arguments))

    def test_path_is_mandatory__with_option(self):
        arguments = args_with_rel_ops('{rel_act_option}')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _just_parse(single_line_source(arguments))

    def test_disallowed_relativities(self):
        for relativity in DISALLOWED_RELATIVITIES:
            for following_lines in [[], ['following line']]:
                with self.subTest(relativity=str(relativity),
                                  following_lines=repr(following_lines)):
                    option_conf = conf_rel_any(relativity)
                    source = remaining_source('{rel_opt} file-name'.format(rel_opt=option_conf.option_string),
                                              following_lines)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        _just_parse(source)

    def test_fail_when_superfluous_arguments__without_option(self):
        arguments = 'expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _just_parse(single_line_source(arguments))

    def test_fail_when_superfluous_arguments__with_option(self):
        arguments = '--rel-act expected-argument superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _just_parse(single_line_source(arguments))


class TestFailingParseWithContents(unittest.TestCase):
    def test_path_is_mandatory__with_option(self):
        arguments = args_with_rel_ops('{rel_act_option} = <<MARKER superfluous ')
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = remaining_source(arguments,
                                      ['MARKER'])
            _just_parse(source)

    def test_disallowed_relativities(self):
        for relativity in DISALLOWED_RELATIVITIES:
            for following_lines in [[], ['following line']]:
                with self.subTest(relativity=str(relativity),
                                  following_lines=repr(following_lines)):
                    option_conf = conf_rel_any(relativity)
                    source = remaining_source(
                        '{rel_opt} file-name = <<MARKER'.format(rel_opt=option_conf.option_string),
                        ['MARKER'] + following_lines)
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        _just_parse(source)

    def test_fail_when_contents_is_missing(self):
        arguments = 'expected-argument = '
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = remaining_source(arguments)
            _just_parse(source)

    def test_fail_when_superfluous_arguments__without_option(self):
        arguments = 'expected-argument = <<MARKER superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            source = remaining_source(arguments,
                                      ['MARKER'])
            _just_parse(source)

    def test_fail_when_superfluous_arguments__with_option(self):
        arguments = args_with_rel_ops('{rel_act_option}  expected-argument <= <MARKER superfluous-argument')
        source = remaining_source(arguments,
                                  ['MARKER'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            _just_parse(source)


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: Expectation,
               phase_is_before_act: bool = True,
               ):
        parser = sut.EmbryoParser('instruction-name', phase_is_before_act)
        embryo_check.check(self, parser, source, arrangement, expectation)


class TestCommonFailingScenariosDueToInvalidDestinationFile(TestCaseBase):
    def _check_cases_for_dst_file_setup(self,
                                        dst_file_name: str,
                                        dst_root_contents_before_execution: DirContents,
                                        ):
        # ARRANGE #

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

        src_file = PathArgumentWithRelativity('src-file.txt',
                                              conf_rel_home(RelHomeOptionType.REL_HOME_CASE))

        file_contents_arguments_constructor = TransformableContentsConstructor(
            file(src_file.file_name, src_file.relativity)
        )

        src_file_in_home_contents = src_file.relativity.populator_for_relativity_option_root(
            DirContents([empty_file(src_file.file_name)])
        )

        file_contents_cases = [
            NameAndValue(
                'empty file',
                empty_file_arguments()
            ),
            NameAndValue(
                'contents of here doc',
                here_document_contents_arguments(['contents'])
            ),
            NameAndValue(
                'contents of output from shell command / without transformation',
                shell_contents_arguments_constructor.without_transformation()
            ),
            NameAndValue(
                'contents of output from shell command / with transformation',
                shell_contents_arguments_constructor.with_transformation(arbitrary_transformer.name)
            ),
            NameAndValue(
                'contents of existing file / without transformation',
                file_contents_arguments_constructor.without_transformation()
            ),
            NameAndValue(
                'contents of existing file / with transformation',
                file_contents_arguments_constructor.with_transformation(arbitrary_transformer.name)
            ),
        ]

        dst_file_relativity_cases = [
            conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
            conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
        ]

        for rel_opt_conf in dst_file_relativity_cases:

            non_home_contents = rel_opt_conf.populator_for_relativity_option_root__non_home(
                dst_root_contents_before_execution)

            for file_contents_case in file_contents_cases:
                optional_arguments = file_contents_case.value
                assert isinstance(optional_arguments, Arguments)  # Type info for IDE

                with self.subTest(file_contents_variant=file_contents_case.name,
                                  first_line_argments=optional_arguments.first_line,
                                  dst_file_variant=rel_opt_conf.option_string):
                    source = remaining_source(
                        '{relativity_option_arg} {dst_file_argument} {optional_arguments}'.format(
                            relativity_option_arg=rel_opt_conf.option_string,
                            dst_file_argument=dst_file_name,
                            optional_arguments=optional_arguments.first_line,
                        ),
                        optional_arguments.following_lines)

                    # ACT & ASSERT #

                    self._check(source,
                                ArrangementWithSds(
                                    pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                                    home_or_sds_contents=src_file_in_home_contents,
                                    non_home_contents=non_home_contents,
                                    symbols=symbols,
                                ),
                                Expectation(
                                    main_result=is_failure(),
                                    symbol_usages=asrt.anything_goes(),
                                )
                                )

    def test_fail_WHEN_dst_file_is_existing_file(self):
        self._check_cases_for_dst_file_setup(
            'file',
            DirContents([
                empty_file('file')
            ]),
        )

    def test_file_WHEN_dst_file_is_existing_dir(self):
        self._check_cases_for_dst_file_setup(
            'existing-dir',
            DirContents([
                empty_dir('existing-dir')
            ]),
        )

    def test_file_WHEN_dst_file_is_existing_broken_symlink(self):
        self._check_cases_for_dst_file_setup(
            'existing-dir',
            DirContents([
                fs.sym_link('existing-symlink.txt',
                            'non-existing-symlink-target.txt')
            ]),
        )

    def test_fail_WHEN_dst_file_is_under_path_that_contains_a_component_that_is_an_existing_file(self):
        self._check_cases_for_dst_file_setup(
            'existing-dir/existing-file/dst-file-name',
            DirContents([
                Dir('existing-dir', [
                    empty_file('existing-file')
                ])
            ]),
        )


class TestSuccessfulScenariosWithNoContents(TestCaseBase):
    def test_single_file_in_root_dir(self):
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                file_name = 'file-name.txt'
                expected_file = fs.empty_file(file_name)
                self._check(
                    remaining_source('{relativity_option} {file_name}'.format(
                        relativity_option=rel_opt_conf.option_string,
                        file_name=file_name)),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                    ),
                    Expectation(
                        main_result=is_success(),
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_list,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(rel_opt_conf.root_dir__non_home,
                                                                               fs.DirContents([expected_file])),
                    ))

    def test_single_file_in_non_existing_sub_dir(self):
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                sub_dir_name = 'sub-dir'
                expected_file = fs.empty_file('file-name.txt')
                self._check(
                    remaining_source('{relativity_option} {sub_dir}/{file_name}'.format(
                        relativity_option=rel_opt_conf.option_string,
                        sub_dir=sub_dir_name,
                        file_name=expected_file.file_name)),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                    ),
                    Expectation(
                        main_result=is_success(),
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_list,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(
                            rel_opt_conf.root_dir__non_home,
                            fs.DirContents([fs.Dir(sub_dir_name,
                                                   [expected_file])])),
                    ))

    def test_single_file_in_existing_sub_dir(self):
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                sub_dir_name = 'sub-dir'
                expected_file = fs.empty_file('file-name.txt')
                self._check(
                    remaining_source('{relativity_option} {sub_dir}/{file_name}'.format(
                        relativity_option=rel_opt_conf.option_string,
                        sub_dir=sub_dir_name,
                        file_name=expected_file.file_name)),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                        non_home_contents=rel_opt_conf.populator_for_relativity_option_root__non_home(
                            fs.DirContents([fs.empty_dir(sub_dir_name)])
                        )
                    ),
                    Expectation(
                        main_result=is_success(),
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_list,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(
                            rel_opt_conf.root_dir__non_home,
                            fs.DirContents([fs.Dir(sub_dir_name,
                                                   [expected_file])])),
                    ))


class TestSuccessfulScenariosWithConstantContents(TestCaseBase):
    def test_contents_from_here_doc(self):
        here_doc_line = 'single line in here doc'
        expected_file_contents = here_doc_line + '\n'
        expected_file = fs.File('a-file-name.txt', expected_file_contents)
        for rel_opt_conf in ALLOWED_RELATIVITIES:
            with self.subTest(relativity_option_string=rel_opt_conf.option_string):
                self._check(
                    remaining_source(
                        '{rel_opt} {file_name} = <<THE_MARKER'.format(rel_opt=rel_opt_conf.option_string,
                                                                      file_name=expected_file.file_name),
                        [here_doc_line,
                         'THE_MARKER']),
                    ArrangementWithSds(
                        pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                    ),
                    Expectation(
                        main_result=is_success(),
                        side_effects_on_home=f_asrt.dir_is_empty(),
                        symbol_usages=asrt.is_empty_list,
                        main_side_effects_on_sds=non_home_dir_contains_exactly(rel_opt_conf.root_dir__non_home,
                                                                               fs.DirContents([expected_file])),
                    ))


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
        src_file_rel_option = RelOptionType.REL_HOME_CASE

        expected_dst_file = fs.File('dst-file-name.txt', src_file.contents.upper())
        dst_file_symbol = NameAndValue('DST_FILE_SYMBOL', expected_dst_file.name)
        dst_file_rel_option = RelOptionType.REL_TMP

        file_contents_arg = TransformableContentsConstructor(
            file(symbol_reference_syntax_for_name(src_file.name))
        ).with_transformation(to_upper_transformer.name)

        source = remaining_source(
            '{file_name} {content_arguments}'.format(
                file_name=symbol_reference_syntax_for_name(dst_file_symbol.name),
                content_arguments=file_contents_arg.first_line
            ),
            file_contents_arg.following_lines)

        symbols = SymbolTable({
            src_file_symbol.name:
                container(resolver_of_rel_option(src_file_rel_option,
                                                 PathPartAsFixedPath(src_file_symbol.value))),

            dst_file_symbol.name:
                container(resolver_of_rel_option(dst_file_rel_option,
                                                 PathPartAsFixedPath(dst_file_symbol.value))),

            to_upper_transformer.name:
                container(to_upper_transformer.value),
        })

        # ACT & ASSERT #

        self._check(source,
                    ArrangementWithSds(
                        symbols=symbols,
                    ),
                    Expectation(
                        main_result=is_success(),
                        symbol_usages=asrt.matches_sequence([

                            equals_symbol_reference(
                                SymbolReference(dst_file_symbol.name,
                                                file_ref_or_string_reference_restrictions(
                                                    sut.REL_OPT_ARG_CONF.options.accepted_relativity_variants))
                            ),

                            is_lines_transformer_reference_to(to_upper_transformer.name),

                            SymbolReference(src_file_symbol.name,
                                            file_ref_or_string_reference_restrictions(
                                                sut.SRC_OPT_ARG_CONF.options.accepted_relativity_variants))
                            ,
                        ]),
                    )
                    )

    @staticmethod
    def _expect_failure_in(step_of_expected_failure: Step) -> Expectation:
        symbol_usages_expectation = asrt.is_list_of(asrt.is_instance(SymbolReference))

        if step_of_expected_failure is Step.VALIDATE_PRE_SDS:
            return Expectation(validation_pre_sds=IS_FAILURE_OF_VALIDATION,
                               symbol_usages=symbol_usages_expectation)
        else:
            return Expectation(main_result=IS_FAILURE_OF_MAIN,
                               symbol_usages=symbol_usages_expectation)

    def _check_of_invalid_src_file(self,
                                   is_before_act_2_every_src_file_rel_conf: types.FunctionType,
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

        for phase_is_before_act in [False, True]:
            for src_file_rel_conf in is_before_act_2_every_src_file_rel_conf(phase_is_before_act):
                src_file = PathArgumentWithRelativity(self.src_file_name,
                                                      src_file_rel_conf)
                args_constructor = TransformableContentsConstructor(
                    file(self.src_file_name, src_file_rel_conf)
                )
                for src_file_variant in self.src_file_variants:
                    for contents_arguments in args_constructor.with_and_without_transformer_cases(transformer.name):
                        arguments = complete_arguments(dst_file, contents_arguments)
                        source = source_of(arguments)
                        with self.subTest(phase_is_before_act=phase_is_before_act,
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
                                expectation)

    def test_validation_pre_sds_SHOULD_fail_WHEN_source_is_not_an_existing_file_rel_home(self):
        self._check_of_invalid_src_file(lambda x: every_conf_rel_home(),
                                        Step.VALIDATE_PRE_SDS)

    def test_main_result_SHOULD_be_failure_WHEN_source_is_not_an_existing_file_rel_non_home(self):
        def every_src_file_rel_conf(is_before_act: bool):
            return [
                conf_rel_non_home(relativity)
                for relativity in accepted_non_home_source_relativities(is_before_act)
            ]

        self._check_of_invalid_src_file(every_src_file_rel_conf, Step.MAIN)

    def test_all_relativities__without_transformer(self):
        # ARRANGE #

        source_file = fs.File('source-file.txt', 'contents of source file')
        expected_file = fs.File('a-file-name.txt', source_file.contents)

        for dst_rel_opt_conf in ALLOWED_RELATIVITIES:
            for src_rel_opt_conf in ALLOWED_SOURCE_FILE_RELATIVITIES:
                file_contents_arg = TransformableContentsConstructor(
                    file(source_file.name, src_rel_opt_conf)
                ).without_transformation()

                with self.subTest(relativity_option_string=dst_rel_opt_conf.option_string):
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
                                DirContents([source_file]))
                        ),
                        Expectation(
                            main_result=is_success(),
                            side_effects_on_home=f_asrt.dir_is_empty(),
                            symbol_usages=asrt.is_empty_list,
                            main_side_effects_on_sds=non_home_dir_contains_exactly(dst_rel_opt_conf.root_dir__non_home,
                                                                                   fs.DirContents([expected_file])),
                        ))

    def test_all_relativities__with_transformer(self):
        # ARRANGE #

        source_file = fs.File('source-file.txt', 'contents of source file')
        expected_file = fs.File('a-file-name.txt', source_file.contents.upper())

        to_upper_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            LinesTransformerResolverConstantTestImpl(MyToUppercaseTransformer()))
        symbols = SymbolTable({
            to_upper_transformer.name:
                container(to_upper_transformer.value),
        })

        for dst_rel_opt_conf in ALLOWED_RELATIVITIES:
            for src_rel_opt_conf in ALLOWED_SOURCE_FILE_RELATIVITIES:
                file_contents_arg = TransformableContentsConstructor(
                    file(source_file.name, src_rel_opt_conf)
                ).with_transformation(to_upper_transformer.name)

                with self.subTest(relativity_option_string=dst_rel_opt_conf.option_string):
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
                                DirContents([source_file])),
                            symbols=symbols,
                        ),
                        Expectation(
                            main_result=is_success(),
                            main_side_effects_on_sds=non_home_dir_contains_exactly(dst_rel_opt_conf.root_dir__non_home,
                                                                                   fs.DirContents([expected_file])),
                            symbol_usages=asrt.matches_sequence([
                                is_lines_transformer_reference_to(to_upper_transformer.name),
                            ])
                        ))


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
                        main_result=is_success(),
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

        for rel_opt_conf in ALLOWED_RELATIVITIES:
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
                        main_result=is_success(),
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
                main_result=is_success(),
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
                        main_result=is_failure(),
                    ))


class TestSymbolReferences(TestCaseBase):
    def test_symbol_reference_in_file_argument(self):
        sub_dir_name = 'sub-dir'
        relativity = RelOptionType.REL_ACT
        symbol = NameAndValue('symbol_name',
                              file_refs.of_rel_option(relativity,
                                                      PathPartAsFixedPath(sub_dir_name)))
        expected_symbol_reference = SymbolReference(
            symbol.name,
            parse_file_ref.path_or_string_reference_restrictions(
                ACCEPTED_RELATIVITY_VARIANTS
            ))
        here_doc_line = 'single line in here doc'
        expected_file_contents = here_doc_line + '\n'
        expected_file = fs.File('a-file-name.txt', expected_file_contents)
        self._check(
            remaining_source(
                '{symbol_ref}/{file_name} = <<THE_MARKER'.format(
                    symbol_ref=symbol_reference_syntax_for_name(symbol.name),
                    file_name=expected_file.file_name,
                ),
                [here_doc_line,
                 'THE_MARKER']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                symbols=data_symbol_utils.symbol_table_with_single_file_ref_value(
                    symbol.name,
                    symbol.value),
            ),
            Expectation(
                main_result=is_success(),
                symbol_usages=equals_symbol_references([expected_symbol_reference]),
                main_side_effects_on_sds=dir_contains_exactly(
                    relativity,
                    fs.DirContents([
                        fs.Dir(sub_dir_name, [expected_file])])),
            ))

    def test_symbol_reference_in_file_argument_and_here_document(self):
        sub_dir_name = 'sub-dir'
        relativity = RelOptionType.REL_ACT
        file_symbol = NameAndValue('file_symbol_name',
                                   file_refs.of_rel_option(relativity,
                                                           PathPartAsFixedPath(sub_dir_name)))
        here_doc_symbol = NameAndValue('here_doc_symbol_name',
                                       'here doc symbol value')

        expected_file_symbol_reference = SymbolReference(
            file_symbol.name,
            parse_file_ref.path_or_string_reference_restrictions(
                ACCEPTED_RELATIVITY_VARIANTS))
        expected_here_doc_symbol_reference = SymbolReference(
            here_doc_symbol.name,
            is_any_data_type())

        here_doc_line_template = 'pre symbol {symbol} post symbol'

        expected_file_contents = here_doc_line_template.format(symbol=here_doc_symbol.value) + '\n'

        expected_file = fs.File('a-file-name.txt', expected_file_contents)

        expected_symbol_references = [expected_file_symbol_reference,
                                      expected_here_doc_symbol_reference]

        symbol_table = data_symbol_utils.SymbolTable({
            file_symbol.name: data_symbol_utils.file_ref_constant_container(file_symbol.value),
            here_doc_symbol.name: data_symbol_utils.string_constant_container(here_doc_symbol.value),
        })

        self._check(
            remaining_source(
                '{symbol_ref}/{file_name} = <<THE_MARKER'.format(
                    symbol_ref=symbol_reference_syntax_for_name(file_symbol.name),
                    file_name=expected_file.file_name,
                ),
                [here_doc_line_template.format(
                    symbol=symbol_reference_syntax_for_name(here_doc_symbol.name)),
                    'THE_MARKER']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
                symbols=symbol_table,
            ),
            Expectation(
                main_result=is_success(),
                symbol_usages=equals_symbol_references(expected_symbol_references),
                main_side_effects_on_sds=dir_contains_exactly(
                    relativity,
                    fs.DirContents([
                        fs.Dir(sub_dir_name, [expected_file])])),
            ))


class TestParserConsumptionOfSource(TestCaseBase):
    def test_last_line__no_contents(self):
        expected_file = fs.empty_file('a-file-name.txt')
        self._check(
            remaining_source(
                '{file_name}'.format(file_name=expected_file.file_name),
            ),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
            ),
            Expectation(
                main_result=is_success(),
                source=source_is_at_end,
            ),
        )

    def test_not_last_line__no_contents(self):
        expected_file = fs.empty_file('a-file-name.txt')
        self._check(
            remaining_source(
                '{file_name}'.format(file_name=expected_file.file_name),
                ['following line']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
            ),
            Expectation(
                main_result=is_success(),
                source=is_at_beginning_of_line(2),
            ),
        )

    def test_last_line__contents(self):
        expected_file = fs.empty_file('a-file-name.txt')
        hd_args = here_document_contents_arguments([])
        self._check(
            remaining_source(
                '{file_name} {hd_args}'.format(
                    file_name=expected_file.file_name,
                    hd_args=hd_args.first_line,
                ),
                hd_args.following_lines),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
            ),
            Expectation(
                main_result=is_success(),
                source=source_is_at_end,
            ),
        )

    def test_not_last_line__contents(self):
        expected_file = fs.empty_file('a-file-name.txt')

        hd_args = here_document_contents_arguments([])
        self._check(
            remaining_source(
                '{file_name} {hd_args}'.format(
                    file_name=expected_file.file_name,
                    hd_args=hd_args.first_line,
                ),
                hd_args.following_lines + ['following line']),
            ArrangementWithSds(
                pre_contents_population_action=SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR,
            ),
            Expectation(
                main_result=is_success(),
                source=is_at_beginning_of_line(3),
            ),
        )


def _just_parse(source: ParseSource,
                phase_is_before_act: bool = True, ):
    sut.EmbryoParser('the-instruction-name', phase_is_before_act).parse(source)


class Arguments:
    def __init__(self, first_line: str, following_lines: list):
        self.first_line = first_line
        self.following_lines = following_lines


def empty_file_arguments() -> Arguments:
    return Arguments('', [])


def here_document_contents_arguments(lines: list) -> Arguments:
    return Arguments('= <<EOF',
                     lines + ['EOF'])


def stdout_from(program: Arguments) -> Arguments:
    return Arguments(option_syntax(sut.STDOUT_OPTION) + ' ' + program.first_line,
                     program.following_lines)


def shell_command(command_line: str) -> Arguments:
    return Arguments(sut.SHELL_COMMAND_TOKEN + ' ' + command_line,
                     [])


def file(file_name: str,
         rel_option: RelativityOptionConfiguration = None) -> Arguments:
    args = [option_syntax(sut.FILE_OPTION)]
    if rel_option is not None:
        args.append(rel_option.option_string)
    args.append(file_name)
    return Arguments(' '.join(args),
                     [])


class TransformableContentsConstructor:
    def __init__(self, after_transformer: Arguments):
        self.after_transformer = after_transformer

    def without_transformation(self) -> Arguments:
        return Arguments('= ' + self.after_transformer.first_line,
                         self.after_transformer.following_lines)

    def with_transformation(self, transformer: str) -> Arguments:
        first_line = ' '.join([
            '=',
            option_syntax(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            transformer,
            self.after_transformer.first_line
        ])

        return Arguments(first_line,
                         self.after_transformer.following_lines)

    def with_and_without_transformer_cases(self, transformer_expr: str) -> list:
        return [
            self.without_transformation(),
            self.with_transformation(transformer_expr),
        ]


def complete_arguments(dst_file: PathArgumentWithRelativity,
                       contents_arguments: Arguments) -> Arguments:
    return Arguments(dst_file.argument_str + ' ' + contents_arguments.first_line,
                     contents_arguments.following_lines)


def source_of(arguments: Arguments) -> ParseSource:
    return remaining_source(arguments.first_line,
                            arguments.following_lines)


def complete_source(dst_file: PathArgumentWithRelativity,
                    contents_arguments: Arguments) -> ParseSource:
    return source_of(complete_arguments(dst_file, contents_arguments))


IS_FAILURE_OF_VALIDATION = asrt.is_instance(str)

IS_FAILURE_OF_MAIN = asrt.is_instance(str)
IS_SUCCESS_OF_MAIN = asrt.is_none


def src_path_relativity_variants(phase_is_before_act: bool) -> PathRelativityVariants:
    return PathRelativityVariants(
        accepted_source_relativities(phase_is_before_act),
        True)


DST_PATH_RELATIVITY_VARIANTS = PathRelativityVariants(
    {
        RelOptionType.REL_CWD,
        RelOptionType.REL_ACT,
        RelOptionType.REL_TMP,
    },
    False)


def accepted_source_relativities(phase_is_before_act: bool) -> set:
    if phase_is_before_act:
        return set(RelOptionType).difference({RelOptionType.REL_RESULT})
    else:
        return set(RelOptionType)


def accepted_non_home_source_relativities(phase_is_before_act: bool) -> set:
    if phase_is_before_act:
        return set(RelNonHomeOptionType).difference({RelNonHomeOptionType.REL_RESULT})
    else:
        return set(RelNonHomeOptionType)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
