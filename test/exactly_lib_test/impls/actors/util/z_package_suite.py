import unittest

from exactly_lib_test.impls.actors.util import source_code_lines, parse_act_interpreter
from exactly_lib_test.impls.actors.util.actor_from_parts import z_package_suite as executor_made_of_parts


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        executor_made_of_parts.suite(),
        source_code_lines.suite(),
        parse_act_interpreter.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
