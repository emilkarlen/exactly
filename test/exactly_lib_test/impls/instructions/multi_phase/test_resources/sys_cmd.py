from exactly_lib_test.impls.types.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.strings import WithToString


def command_line(program: WithToString,
                 arguments: ArgumentElementsRenderer = ab.empty(),
                 ) -> ArgumentElementsRenderer:
    return ab.sequence__r([
        ab.singleton(program),
        arguments,
    ])
