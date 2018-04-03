from exactly_lib.help_texts import instruction_arguments
from exactly_lib.instructions.utils.parse import parse_file_maker
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_case_utils.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.test_resources.arguments_building import Stringable


def from_program(file: Stringable,
                 output_variant: ProcOutputFile,
                 program: ArgumentElements,
                 transformation: Stringable = None) -> ArgumentElements:
    program_with_pgm_option = program.prepend_to_first_line([ab.option(parse_file_maker.STDOUT_OPTION)])

    ret_val = ArgumentElements([file, instruction_arguments.ASSIGNMENT_OPERATOR])
    if transformation is not None:
        ret_val = ret_val.append_to_first_line([ab.option(instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
                                                transformation
                                                ])
        return ret_val.followed_by_lines(program_with_pgm_option.all_lines)
    else:
        return ret_val.append_to_first_and_following_lines(program_with_pgm_option)


def complete_arguments(dst_file: PathArgumentWithRelativity,
                       contents: Arguments) -> Arguments:
    return Arguments(dst_file.argument_str).followed_by(contents)


def source_of(arguments: Arguments) -> ParseSource:
    return remaining_source(arguments.first_line,
                            arguments.following_lines)
