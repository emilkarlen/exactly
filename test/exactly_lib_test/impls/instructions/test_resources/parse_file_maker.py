from typing import Set, List, Sequence

from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.impls.instructions.utils.file_maker import defs
from exactly_lib.tcfs.path_relativity import PathRelativityVariants, RelOptionType, \
    RelNonHdsOptionType, RelHdsOptionType, RelSdsOptionType
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.types.parse.test_resources import arguments_building as arg_lines
from exactly_lib_test.impls.types.parse.test_resources import arguments_building as parse_args
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.impls.types.test_resources import arguments_building as ab
from exactly_lib_test.impls.types.test_resources.relativity_options import RelativityOptionConfiguration, \
    conf_rel_hds, conf_rel_sds, conf_rel_non_hds, default_conf_rel_non_hds

ALLOWED_SRC_FILE_RELATIVITIES__BEFORE_ACT = [
    conf_rel_hds(RelHdsOptionType.REL_HDS_CASE),
    conf_rel_hds(RelHdsOptionType.REL_HDS_ACT),
    conf_rel_sds(RelSdsOptionType.REL_ACT),
    conf_rel_sds(RelSdsOptionType.REL_TMP),
    conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
    default_conf_rel_non_hds(RelNonHdsOptionType.REL_CWD),
]


def allowed_src_file_relativities(phase_is_after_act: bool) -> Sequence[RelativityOptionConfiguration]:
    return (
        ALLOWED_SRC_FILE_RELATIVITIES__BEFORE_ACT + [conf_rel_sds(RelSdsOptionType.REL_RESULT)]
        if phase_is_after_act
        else
        ALLOWED_SRC_FILE_RELATIVITIES__BEFORE_ACT
    )


def empty_file_contents_arguments() -> ArgumentElements:
    return ArgumentElements([])


def explicit_contents_of(file_maker: ArgumentElements,
                         with_file_maker_on_separate_line: bool = False) -> ArgumentElements:
    assignment_operator = [instruction_arguments.ASSIGNMENT_OPERATOR]
    if with_file_maker_on_separate_line:
        return arg_lines.elements(assignment_operator).followed_by_lines(file_maker.lines)
    else:
        return file_maker.prepend_to_first_line(assignment_operator)


def here_document_contents_arguments(lines: List[str]) -> ArgumentElements:
    return explicit_contents_of(parse_args.here_document_as_elements(lines))


def string_contents_arguments(string: str) -> ArgumentElements:
    return explicit_contents_of(parse_args.string_as_elements(string))


def string_contents(string: str) -> ArgumentElements:
    return parse_args.string_as_elements(string)


def output_from_program(program_output_channel: ProcOutputFile,
                        program: ArgumentElements,
                        ignore_exit_code: bool = False,
                        with_new_line_after_source_type_option: bool = False) -> ArgumentElements:
    program_output_option = [
        ab.option(defs.PROGRAM_OUTPUT_OPTIONS[program_output_channel])
    ]
    if ignore_exit_code:
        program_output_option.append(
            ab.option(defs.IGNORE_EXIT_CODE)
        )

    if with_new_line_after_source_type_option:
        return ArgumentElements(program_output_option,
                                program.all_lines)
    else:
        return program.prepend_to_first_line(program_output_option)


def file_with_rel_opt_conf(file_name: str,
                           rel_option: RelativityOptionConfiguration = None,
                           with_new_line_after_source_type_option: bool = False) -> ArgumentElements:
    first_line = [ab.option(defs.FILE_OPTION)]
    following_line_args = []

    file_args = first_line
    if with_new_line_after_source_type_option:
        file_args = following_line_args

    if rel_option is not None:
        file_args.append(rel_option.path_argument_of_rel_name(file_name))
    else:
        file_args.append(file_name)

    following_lines = [] \
        if not with_new_line_after_source_type_option \
        else [following_line_args]

    return ArgumentElements(first_line,
                            following_lines)


class TransformableContentsConstructor:
    def __init__(self,
                 non_transformer_arguments: ArgumentElements):
        self._non_transformer_arguments = non_transformer_arguments

    def without_transformation(self, with_file_maker_on_separate_line: bool = False) -> ArgumentElements:
        return explicit_contents_of(self._non_transformer_arguments,
                                    with_file_maker_on_separate_line=with_file_maker_on_separate_line)

    def with_transformation(self,
                            transformer: str,
                            with_file_maker_on_separate_line: bool = False,
                            with_transformer_on_separate_line: bool = True
                            ) -> ArgumentElements:
        transformer_elements = [
            ab.option(string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            transformer,
        ]

        if with_transformer_on_separate_line:
            transformer_arguments = ArgumentElements([], [transformer_elements])
        else:
            transformer_arguments = ArgumentElements(transformer_elements)
        args = self._non_transformer_arguments.last_line_followed_by(transformer_arguments)
        return explicit_contents_of(args,
                                    with_file_maker_on_separate_line=with_file_maker_on_separate_line)

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


def accepted_non_hds_source_relativities(phase_is_after_act: bool) -> Set[RelNonHdsOptionType]:
    if phase_is_after_act:
        return set(RelNonHdsOptionType)
    else:
        return set(RelNonHdsOptionType).difference({RelNonHdsOptionType.REL_RESULT})
