import unittest

from exactly_lib_test.type_val_prims.matcher import z_package_suite as matcher
from exactly_lib_test.type_val_prims.program import z_package_suite as program
from exactly_lib_test.type_val_prims.string_model import z_package_suite as string_models
from exactly_lib_test.type_val_prims.string_transformer import z_package_suite as string_transformer
from exactly_lib_test.type_val_prims.trace import z_package_suite as trace


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        trace.suite(),
        string_models.suite(),
        string_transformer.suite(),
        matcher.suite(),
        program.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
