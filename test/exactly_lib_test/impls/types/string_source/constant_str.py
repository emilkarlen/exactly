import unittest
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.impls.types.string_source import constant_str as sut
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.string_source.test_resources.dir_file_space_getter import \
    dir_file_space_for_single_usage_getter
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import \
    SourceConstructorWAppEnvForTest


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        Test(),
    ])


class Test(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'empty',
                '',
            ),
            NameAndValue(
                'single line',
                'abc',
            ),
            NameAndValue(
                'multi line',
                '1st\n2nd\n',
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                source_constructor = _SourceConstructor(case.value)
                expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                    ''.join(source_constructor.contents),
                    may_depend_on_external_resources=asrt.equals(False),
                    frozen_may_depend_on_external_resources=asrt.equals(False),
                )

                assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
                # ACT & ASSERT #
                assertion.apply_without_message(
                    self,
                    multi_obj_assertions.SourceConstructors.of_common(source_constructor),
                )


class _SourceConstructor(SourceConstructorWAppEnvForTest):
    def __init__(self, contents: str):
        super().__init__(dir_file_space_for_single_usage_getter)
        self.contents = contents

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        yield sut.string_source(self.contents,
                                app_env.tmp_files_space)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
