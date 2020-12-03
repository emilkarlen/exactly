import unittest
from contextlib import contextmanager
from typing import ContextManager, Sequence

from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib_test.impls.types.string_source.test_resources.dir_file_space_getter import \
    dir_file_space_for_single_usage_getter
from exactly_lib_test.impls.types.string_source.test_resources.string_sources import SourceFromLinesTestImpl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.string_source.test_resources import source_checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestModelFromLinesBase(),
    ])


class TestModelFromLinesBase(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        source_constructor = _SourceConstructor([
            '1st\n',
            '2nd\n',
        ]
        )
        expectation = source_checker.Expectation.equals(
            ''.join(source_constructor.lines),
            may_depend_on_external_resources=asrt.anything_goes(),
        )

        checker = source_checker.Checker(
            self,
            source_constructor,
            expectation,
            dir_file_space_for_single_usage_getter(self),
        )
        # ACT & ASSERT #
        checker.check()


class _SourceConstructor(source_checker.SourceConstructor):
    def __init__(self, lines: Sequence[str]):
        self.lines = lines

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringSource]:
        yield SourceFromLinesTestImpl(self.lines, app_env.tmp_files_space)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
