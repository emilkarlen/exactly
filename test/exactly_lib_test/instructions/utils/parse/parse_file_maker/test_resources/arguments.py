from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.utils.parse import parse_file_maker
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType, \
    RelNonHomeOptionType, RelHomeOptionType, RelSdsOptionType
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments, here_document
from exactly_lib_test.test_case_utils.test_resources.relativity_options import RelativityOptionConfiguration, \
    conf_rel_home, conf_rel_sds, conf_rel_non_home, default_conf_rel_non_home

ALLOWED_SRC_FILE_RELATIVITIES = [
    conf_rel_home(RelHomeOptionType.REL_HOME_CASE),
    conf_rel_home(RelHomeOptionType.REL_HOME_ACT),
    conf_rel_sds(RelSdsOptionType.REL_ACT),
    conf_rel_sds(RelSdsOptionType.REL_TMP),
    conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
    default_conf_rel_non_home(RelNonHomeOptionType.REL_CWD),
]


def empty_file_contents_arguments() -> Arguments:
    return Arguments('', [])


def explicit_contents_of(contents_arguments: Arguments) -> Arguments:
    return Arguments(instruction_arguments.ASSIGNMENT_OPERATOR).followed_by(contents_arguments)


def here_document_contents_arguments(lines: list) -> Arguments:
    return explicit_contents_of(here_document(lines))


def string_contents_arguments(string: str) -> Arguments:
    return explicit_contents_of(Arguments(string))


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
    return Arguments(parse_file_maker.SHELL_COMMAND_TOKEN + ' ' + command_line)


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


class TransformableContentsConstructor:
    def __init__(self,
                 after_transformer: Arguments,
                 with_new_line_after_transformer: bool = False):
        self._with_new_line_after_transformer = with_new_line_after_transformer
        self._after_transformer = after_transformer

    def without_transformation(self) -> Arguments:
        return explicit_contents_of(Arguments(self._after_transformer.first_line,
                                              self._after_transformer.following_lines))

    def with_transformation(self, transformer: str) -> Arguments:
        def args() -> Arguments:
            if self._with_new_line_after_transformer:
                first_line = ' '.join([
                    option_syntax(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
                    transformer,
                ])

                return Arguments(first_line,
                                 [self._after_transformer.first_line] +
                                 self._after_transformer.following_lines)
            else:
                first_line = ' '.join([
                    option_syntax(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
                    transformer,
                    self._after_transformer.first_line
                ])

                return Arguments(first_line,
                                 self._after_transformer.following_lines)

        return explicit_contents_of(args())

    def with_and_without_transformer_cases(self, transformer_expr: str) -> list:
        return [
            self.without_transformation(),
            self.with_transformation(transformer_expr),
        ]


def src_path_relativity_variants(phase_is_after_act: bool) -> PathRelativityVariants:
    return PathRelativityVariants(
        accepted_source_relativities(phase_is_after_act),
        True)


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
