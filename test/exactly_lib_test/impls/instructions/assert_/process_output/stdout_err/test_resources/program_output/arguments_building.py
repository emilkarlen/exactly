from typing import List, Optional

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.impls.instructions.assert_.process_output.defs import OUTPUT_FROM_PROGRAM_OPTION_NAME
from exactly_lib_test.impls.types.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments.arguments_building import ArgumentElements
from exactly_lib_test.test_resources.strings import WithToString


def from_program(program: ArgumentElements,
                 contents_matcher: List[WithToString],
                 transformation: Optional[WithToString] = None) -> ArgumentElements:
    following_lines = [list(contents_matcher)]
    if transformation is not None:
        following_lines.insert(0, [ab.option(
            string_transformer.WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
            transformation
        ])
    return program \
        .prepend_to_first_line([ab.option(OUTPUT_FROM_PROGRAM_OPTION_NAME)]) \
        .followed_by_lines(following_lines)
