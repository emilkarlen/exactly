import unittest

from exactly_lib_test.impls.types.string_transformer import \
    parse_string_transformer
from exactly_lib_test.impls.types.string_transformer import tcds_paths_replacement, case_converters, sequence, identity
from exactly_lib_test.impls.types.string_transformer.filter import z_package_suite as filter_
from exactly_lib_test.impls.types.string_transformer.replace import z_package_suite as replace
from exactly_lib_test.impls.types.string_transformer.run_program import \
    z_package_suite as run_program
from exactly_lib_test.impls.types.string_transformer.sources import \
    z_package_suite as models
from exactly_lib_test.impls.types.string_transformer.strip import \
    z_package_suite as strip
from exactly_lib_test.impls.types.string_transformer.test_resources_test import \
    z_package_suite as test_resources_test


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(test_resources_test.suite())
    ret_val.addTest(models.suite())
    ret_val.addTest(identity.suite())
    ret_val.addTest(replace.suite())
    ret_val.addTest(filter_.suite())
    ret_val.addTest(sequence.suite())
    ret_val.addTest(run_program.suite())
    ret_val.addTest(parse_string_transformer.suite())
    ret_val.addTest(case_converters.suite())
    ret_val.addTest(strip.suite())
    ret_val.addTest(tcds_paths_replacement.suite())
    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
