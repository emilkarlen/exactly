from exactly_lib.definitions import instruction_arguments
from exactly_lib.instructions.utils.parse import parse_file_maker
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.instructions.utils.parse.parse_file_maker.test_resources import arguments as file_maker_args
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements, elements
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_resources.strings import WithToString


def from_program(file: WithToString,
                 output_variant: ProcOutputFile,
                 program: ArgumentElements,
                 transformation: WithToString = None) -> ArgumentElements:
    program_with_pgm_option = program.prepend_to_first_line([
        ab.option(parse_file_maker.PROGRAM_OUTPUT_OPTIONS[output_variant])
    ])

    ret_val = ArgumentElements([file, instruction_arguments.ASSIGNMENT_OPERATOR]) \
        .followed_by(program_with_pgm_option)
    if transformation is None:
        return ret_val
    else:
        return ret_val.followed_by(elements([ab.option(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
                                             transformation
                                             ]))


def complete_arguments(dst_file: PathArgumentWithRelativity,
                       contents: Arguments) -> Arguments:
    return Arguments(dst_file.argument_str).followed_by(contents)


def complete_argument_elements(dst_file: PathArgumentWithRelativity,
                               contents: ArgumentElements) -> ArgumentElements:
    return ArgumentElements([dst_file.as_argument_element]).followed_by(contents)


def complete_arguments_with_explicit_contents(dst_file: PathArgumentWithRelativity,
                                              file_maker: ArgumentElements,
                                              with_file_maker_on_separate_line: bool = False) -> ArgumentElements:
    return ArgumentElements([dst_file.as_argument_element]).followed_by(
        file_maker_args.explicit_contents_of(file_maker,
                                             with_file_maker_on_separate_line=with_file_maker_on_separate_line))


def source_of(arguments: Arguments) -> ParseSource:
    return remaining_source(arguments.first_line,
                            arguments.following_lines)
