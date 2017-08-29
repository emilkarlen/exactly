import unittest

from exactly_lib_test.section_document.parser_implementations.test_resources_test import token_stream_assertions


def suite() -> unittest.TestSuite:
    return token_stream_assertions.suite()
