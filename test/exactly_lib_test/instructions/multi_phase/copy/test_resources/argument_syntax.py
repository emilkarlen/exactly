from typing import Optional

from exactly_lib_test.test_case_file_structure.test_resources.path_arguments import PathArgument
from exactly_lib_test.test_resources import argument_renderer
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer


def copy(src: PathArgument,
         dst: Optional[PathArgument] = None,
         ) -> ArgumentElementsRenderer:
    return (
        src
        if dst is None
        else
        argument_renderer.SequenceOfArguments([src, dst])
    )
