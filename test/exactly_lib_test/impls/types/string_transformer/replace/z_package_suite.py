import unittest

from exactly_lib_test.impls.types.string_transformer.replace import syntax, dep_on_ext_rsrc, \
    apply_on_every_line, apply_on_selected_lines


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        syntax.suite(),
        dep_on_ext_rsrc.suite(),
        apply_on_every_line.suite(),
        apply_on_selected_lines.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
