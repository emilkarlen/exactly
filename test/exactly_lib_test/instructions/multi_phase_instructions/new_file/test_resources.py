import unittest
from enum import Enum

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.multi_phase_instructions import new_file as sut
from exactly_lib.instructions.utils.parse import parse_file_maker
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelHomeOptionType, RelSdsOptionType, \
    RelNonHomeOptionType, PathRelativityVariants
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_file_structure.test_resources.dir_populator import HomeOrSdsPopulator
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import home_and_sds_populators
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_case_utils.test_resources.relativity_options import conf_rel_home, conf_rel_sds, \
    conf_rel_non_home, default_conf_rel_non_home, RelativityOptionConfiguration
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, Dir
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    SETUP_CWD_INSIDE_STD_BUT_NOT_A_STD_DIR
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class Step(Enum):
    VALIDATE_PRE_SDS = 1
    MAIN = 2


DISALLOWED_RELATIVITIES = [
    RelOptionType.REL_RESULT,
    RelOptionType.REL_HOME_CASE,
    RelOptionType.REL_HOME_ACT,
]
ALLOWED_SRC_FILE_RELATIVITIES = [
    conf_rel_home(RelHomeOptionType.REL_HOME_CASE),
    conf_rel_home(RelHomeOptionType.REL_HOME_ACT),
    conf_rel_sds(RelSdsOptionType.REL_ACT),
    conf_rel_sds(RelSdsOptionType.REL_TMP),
    conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
    default_conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
]
ALLOWED_DST_FILE_RELATIVITIES = [
    conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
    conf_rel_non_home(RelNonHomeOptionType.REL_TMP),
    conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
    default_conf_rel_non_home(RelNonHomeOptionType.REL_CWD),

]
ACCEPTED_RELATIVITY_VARIANTS = PathRelativityVariants({RelOptionType.REL_ACT,
                                                       RelOptionType.REL_TMP,
                                                       RelOptionType.REL_CWD},
                                                      absolute=False)


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: Expectation,
               phase_is_after_act: bool = True,
               ):
        parser = sut.EmbryoParser('instruction-name', phase_is_after_act)
        embryo_check.check(self, parser, source, arrangement, expectation)


def just_parse(source: ParseSource,
               phase_is_after_act: bool = True):
    sut.EmbryoParser('the-instruction-name', phase_is_after_act).parse(source)


class Arguments:
    def __init__(self, first_line: str, following_lines: list):
        self.first_line = first_line
        self.following_lines = following_lines

    @property
    def lines(self) -> list:
        return [self.first_line] + self.following_lines

    @property
    def as_single_string(self) -> str:
        return '\n'.join(self.lines)


def complete_arguments(dst_file: PathArgumentWithRelativity,
                       contents: Arguments) -> Arguments:
    return Arguments(dst_file.argument_str + ' ' + contents.first_line,
                     contents.following_lines)


def empty_file_arguments() -> Arguments:
    return Arguments('', [])


def here_document_contents_arguments(lines: list) -> Arguments:
    return Arguments('= <<EOF',
                     lines + ['EOF'])


def string_contents_arguments(string: str) -> Arguments:
    return Arguments('= ' + string, [])


def stdout_from(program: Arguments,
                with_new_line_after_output_option: bool = False) -> Arguments:
    if with_new_line_after_output_option:
        return Arguments(option_syntax(parse_file_maker.STDOUT_OPTION),
                         [program.first_line] + program.following_lines)
    else:
        return Arguments(option_syntax(
            parse_file_maker.STDOUT_OPTION) + ' ' + program.first_line,
                         program.following_lines)


def shell_command(command_line: str) -> Arguments:
    return Arguments(parse_file_maker.SHELL_COMMAND_TOKEN + ' ' + command_line,
                     [])


def file(file_name: str,
         rel_option: RelativityOptionConfiguration = None,
         with_new_line_after_output_option: bool = False) -> Arguments:
    first_line = [option_syntax(parse_file_maker.FILE_OPTION)]
    following_line_args = []

    file_args = first_line
    if with_new_line_after_output_option:
        file_args = following_line_args

    if rel_option is not None:
        file_args.append(rel_option.option_string)
    file_args.append(file_name)

    following_lines = [] \
        if not with_new_line_after_output_option \
        else [' '.join(following_line_args)]

    return Arguments(' '.join(first_line),
                     following_lines)


def complete_arguments(dst_file: PathArgumentWithRelativity,
                       contents_arguments: Arguments) -> Arguments:
    return Arguments(dst_file.argument_str + ' ' + contents_arguments.first_line,
                     contents_arguments.following_lines)


def source_of(arguments: Arguments) -> ParseSource:
    return remaining_source(arguments.first_line,
                            arguments.following_lines)


IS_FAILURE_OF_VALIDATION = asrt.is_instance(str)
IS_FAILURE = asrt.is_instance(str)
IS_SUCCESS = asrt.is_none


def src_path_relativity_variants(phase_is_after_act: bool) -> PathRelativityVariants:
    return PathRelativityVariants(
        accepted_source_relativities(phase_is_after_act),
        True)


DST_PATH_RELATIVITY_VARIANTS = PathRelativityVariants(
    {
        RelOptionType.REL_CWD,
        RelOptionType.REL_ACT,
        RelOptionType.REL_TMP,
    },
    False)


def accepted_source_relativities(phase_is_after_act: bool) -> set:
    if phase_is_after_act:
        return set(RelOptionType).difference({RelOptionType.REL_RESULT})
    else:
        return set(RelOptionType)


def accepted_non_home_source_relativities(phase_is_after_act: bool) -> set:
    if phase_is_after_act:
        return set(RelNonHomeOptionType)
    else:
        return set(RelNonHomeOptionType).difference({RelNonHomeOptionType.REL_RESULT})


class TransformableContentsConstructor:
    def __init__(self,
                 after_transformer: Arguments,
                 with_new_line_after_transformer: bool = False):
        self._with_new_line_after_transformer = with_new_line_after_transformer
        self._after_transformer = after_transformer

    def without_transformation(self) -> Arguments:
        return Arguments('= ' + self._after_transformer.first_line,
                         self._after_transformer.following_lines)

    def with_transformation(self, transformer: str) -> Arguments:
        if self._with_new_line_after_transformer:
            first_line = ' '.join([
                '=',
                option_syntax(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
                transformer,
            ])

            return Arguments(first_line,
                             [self._after_transformer.first_line] +
                             self._after_transformer.following_lines)
        else:
            first_line = ' '.join([
                '=',
                option_syntax(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
                transformer,
                self._after_transformer.first_line
            ])

            return Arguments(first_line,
                             self._after_transformer.following_lines)

    def with_and_without_transformer_cases(self, transformer_expr: str) -> list:
        return [
            self.without_transformation(),
            self.with_transformation(transformer_expr),
        ]


class InvalidDestinationFileTestCasesData:
    def __init__(self,
                 file_contents_cases: list,
                 symbols: SymbolTable,
                 pre_existing_files: HomeOrSdsPopulator = home_and_sds_populators.empty(),
                 ):
        self.file_contents_cases = file_contents_cases
        self.symbols = symbols
        self.pre_existing_files = pre_existing_files


class TestCommonFailingScenariosDueToInvalidDestinationFileBase(TestCaseBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        raise NotImplementedError('abstract method')

    def _check_cases_for_dst_file_setup(self,
                                        dst_file_name: str,
                                        dst_root_contents_before_execution: DirContents,
                                        ):

        cases_data = self._file_contents_cases()

        dst_file_relativity_cases = [
            conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
            conf_rel_non_home(RelNonHomeOptionType.REL_ACT),
        ]

        for rel_opt_conf in dst_file_relativity_cases:

            non_home_contents = rel_opt_conf.populator_for_relativity_option_root__non_home(
                dst_root_contents_before_execution)

            for file_contents_case in cases_data.file_contents_cases:
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
                                    home_or_sds_contents=cases_data.pre_existing_files,
                                    non_home_contents=non_home_contents,
                                    symbols=cases_data.symbols,
                                ),
                                Expectation(
                                    main_result=IS_FAILURE,
                                    symbol_usages=asrt.anything_goes(),
                                )
                                )

    def test_fail_WHEN_dst_file_is_existing_file(self):
        dst_file_name = 'file.txt'
        self._check_cases_for_dst_file_setup(
            dst_file_name,
            DirContents([
                empty_file(dst_file_name)
            ]),
        )

    def test_file_WHEN_dst_file_is_existing_dir(self):
        dst_file_name = 'dst-dir'
        self._check_cases_for_dst_file_setup(
            dst_file_name,
            DirContents([
                empty_dir(dst_file_name)
            ]),
        )

    def test_file_WHEN_dst_file_is_existing_broken_symlink(self):
        dst_file_name = 'dst-file'
        self._check_cases_for_dst_file_setup(
            dst_file_name,
            DirContents([
                fs.sym_link(dst_file_name,
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
