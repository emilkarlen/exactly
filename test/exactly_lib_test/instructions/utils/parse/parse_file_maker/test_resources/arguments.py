from typing import Set, List, Sequence

from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.utils.parse import parse_file_maker
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType, \
    RelNonHomeOptionType, RelHomeOptionType, RelSdsOptionType
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements, \
    here_document_arg_elements
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
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


def empty_file_contents_arguments() -> ArgumentElements:
    return ArgumentElements([])


def explicit_contents_of(contents_arguments: ArgumentElements) -> ArgumentElements:
    return contents_arguments.prepend_to_first_line([instruction_arguments.ASSIGNMENT_OPERATOR])


def here_document_contents_arguments(lines: List[str]) -> ArgumentElements:
    return explicit_contents_of(here_document_arg_elements(lines))


def string_contents_arguments(string: str) -> ArgumentElements:
    return explicit_contents_of(ArgumentElements([string]))


def output_from_program(program_output_channel: ProcOutputFile,
                        program: ArgumentElements,
                        with_new_line_after_output_option: bool = False) -> ArgumentElements:
    program_output_option = [ab.option(parse_file_maker.PROGRAM_OUTPUT_OPTIONS[program_output_channel])]

    if with_new_line_after_output_option:
        return ArgumentElements(program_output_option,
                                program.all_lines)
    else:
        return program.prepend_to_first_line(program_output_option)


def file(file_name: str,
         rel_option: RelativityOptionConfiguration = None,
         with_new_line_after_output_option: bool = False) -> ArgumentElements:
    first_line = [ab.option(parse_file_maker.FILE_OPTION)]
    following_line_args = []

    file_args = first_line
    if with_new_line_after_output_option:
        file_args = following_line_args

    if rel_option is not None:
        file_args.append(rel_option.file_argument_with_option(file_name))
    else:
        file_args.append(file_name)

    following_lines = [] \
        if not with_new_line_after_output_option \
        else [following_line_args]

    return ArgumentElements(first_line,
                            following_lines)


class TransformableContentsConstructor:
    def __init__(self,
                 non_transformer_arguments: ArgumentElements,
                 with_new_line_before_transformer: bool = True):
        self._with_new_line_before_transformer = with_new_line_before_transformer
        self._non_transformer_arguments = non_transformer_arguments

    def without_transformation(self) -> ArgumentElements:
        return explicit_contents_of(self._non_transformer_arguments)

    def with_transformation(self, transformer: str) -> ArgumentElements:
        transformer_elements = [
            ab.option(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            transformer,
        ]

        if self._with_new_line_before_transformer:
            transformer_arguments = ArgumentElements([], [transformer_elements])
        else:
            transformer_arguments = ArgumentElements(transformer_elements)
        args = self._non_transformer_arguments.last_line_followed_by(transformer_arguments)
        return explicit_contents_of(args)

    def with_and_without_transformer_cases(self, transformer_expr: str) -> Sequence[ArgumentElements]:
        return [
            self.without_transformation(),
            self.with_transformation(transformer_expr),
        ]


def src_path_relativity_variants(phase_is_after_act: bool) -> PathRelativityVariants:
    return PathRelativityVariants(
        accepted_source_relativities(phase_is_after_act),
        True)


def accepted_source_relativities(phase_is_after_act: bool) -> Set[RelOptionType]:
    if phase_is_after_act:
        return set(RelOptionType).difference({RelOptionType.REL_RESULT})
    else:
        return set(RelOptionType)


def accepted_non_home_source_relativities(phase_is_after_act: bool) -> Set[RelNonHomeOptionType]:
    if phase_is_after_act:
        return set(RelNonHomeOptionType)
    else:
        return set(RelNonHomeOptionType).difference({RelNonHomeOptionType.REL_RESULT})
