from exactly_lib.test_case_utils.program import syntax_elements
from exactly_lib_test.tcfs.test_resources.path_arguments import PathArgument
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString


def simple(argument: WithToString) -> ArgumentElementsRenderer:
    return ab.singleton(argument)


def existing_file(path: PathArgument) -> ArgumentElementsRenderer:
    return ab.sequence__r([
        ab.option(syntax_elements.EXISTING_FILE_OPTION_NAME),
        path,
    ])


def existing_dir(path: PathArgument) -> ArgumentElementsRenderer:
    return ab.sequence__r([
        ab.option(syntax_elements.EXISTING_DIR_OPTION_NAME),
        path,
    ])


def existing_path(path: PathArgument) -> ArgumentElementsRenderer:
    return ab.sequence__r([
        ab.option(syntax_elements.EXISTING_PATH_OPTION_NAME),
        path,
    ])


def remaining_part_of_current_line_as_literal(remaining_part_of_current_line: WithToString,
                                              ) -> ArgumentElementsRenderer:
    return ab.sequence([
        syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER,
        remaining_part_of_current_line,
    ])
