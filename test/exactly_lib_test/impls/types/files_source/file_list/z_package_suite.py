import unittest

from exactly_lib_test.impls.types.files_source.file_list import invalid_syntax, illegal_destination_path, \
    symbol_references, individual_file_spec, multiple_file_spec, validation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        invalid_syntax.suite(),
        validation.suite(),
        illegal_destination_path.suite(),
        individual_file_spec.suite(),
        multiple_file_spec.suite(),
        symbol_references.suite(),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
