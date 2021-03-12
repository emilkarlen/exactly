import unittest

from exactly_lib_test.impls.types.files_source import invalid_syntax, illegal_destination_path, individual_file_spec, \
    multiple_file_spec, reference, symbol_references, validation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax.suite(),
        validation.suite(),
        reference.suite(),
        illegal_destination_path.suite(),
        individual_file_spec.suite(),
        multiple_file_spec.suite(),
        symbol_references.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
