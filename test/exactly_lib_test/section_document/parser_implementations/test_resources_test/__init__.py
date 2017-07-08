import unittest

from exactly_lib_test.section_document.parser_implementations.test_resources_test import assert_token_stream


def suite() -> unittest.TestSuite:
    return assert_token_stream.suite()
