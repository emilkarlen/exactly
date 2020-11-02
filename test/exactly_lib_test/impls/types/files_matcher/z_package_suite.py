import unittest

from exactly_lib_test.impls.types.files_matcher import common, empty, num_files, quant_over_files, \
    selections, std_expr, prune
from exactly_lib_test.impls.types.files_matcher.files_condition_containment import \
    z_package_suite as files_condition_containment
from exactly_lib_test.impls.types.files_matcher.models import z_package_suite as models


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        models.suite(),
        common.suite(),
        std_expr.suite(),
        empty.suite(),
        num_files.suite(),
        quant_over_files.suite(),
        selections.suite(),
        prune.suite(),
        files_condition_containment.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
