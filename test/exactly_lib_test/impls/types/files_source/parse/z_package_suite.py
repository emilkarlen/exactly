import unittest

from exactly_lib_test.impls.types.files_source.parse import reference, validation, illegal_destination_path, \
    individual_file_spec, multiple_file_spec, symbol_references


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        validation.suite(),
        reference.suite(),
        illegal_destination_path.suite(),
        individual_file_spec.suite(),
        multiple_file_spec.suite(),
        symbol_references.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
