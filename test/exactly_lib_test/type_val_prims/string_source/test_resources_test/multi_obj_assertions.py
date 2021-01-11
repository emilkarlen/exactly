import unittest
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources import test_of_test_resources_util as test_utils
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_prims.string_source.test_resources import contents_assertions as asrt_str_src_contents, \
    string_source_contents
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions as sut
from exactly_lib_test.type_val_prims.string_source.test_resources import string_sources
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import \
    SourceConstructorWAppEnvForTest
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_base import StringSourceTestImplBase
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_contents import StringSourceContentsData
from exactly_lib_test.type_val_prims.string_source.test_resources_test import test_resources
from exactly_lib_test.type_val_prims.string_source.test_resources_test.test_resources import StringSourceData, \
    ConstructorOfStringSourceData, check_variants


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestExpectedData(),
        TestUnexpectedDataBeforeFreeze(),
        TestInvalidLineSequenceIsDetectedInDataBeforeFreeze(),
        TestUnexpectedDataAfterFreeze(),
        TestInvalidLineSequenceIsDetectedInDataAfterFreeze(),

        TestExpectedHardErrorInContentsMethod(),
        TestExpectedHardErrorExternalDependencies(),
        TestUnexpectedHardErrorInContentsMethod(),

        TestHardErrorShouldNeverHappenInFreeze(),
    ])


class TestExpectedData(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        may_depend_on_external_resources = False
        contents = 'the contents'
        expectation = sut.ExpectationOnUnFrozenAndFrozen.equals(
            contents,
            may_depend_on_external_resources=asrt.equals(may_depend_on_external_resources),
            frozen_may_depend_on_external_resources=asrt.equals(may_depend_on_external_resources),
        )
        data__before_and_after_freeze = StringSourceData(contents, may_depend_on_external_resources)
        source_constructor = ConstructorOfStringSourceData(
            data__before_and_after_freeze,
            data__before_and_after_freeze,
        )
        for checker_variant in check_variants(expectation):
            with self.subTest(checker_variant.name):
                # ACT & ASSERT #
                checker_variant.value.apply(
                    self,
                    sut.SourceConstructors.of_common(source_constructor),
                    asrt.MessageBuilder(),
                )


class TestUnexpectedDataBeforeFreeze(test_resources.TestUnexpectedDataBase):
    def _source_constructor(self,
                            expected: StringSourceData,
                            unexpected: StringSourceData,
                            ) -> sut.SourceConstructor:
        return ConstructorOfStringSourceData(unexpected, expected)


class TestUnexpectedDataAfterFreeze(test_resources.TestUnexpectedDataBase):
    def _source_constructor(self,
                            expected: StringSourceData,
                            unexpected: StringSourceData,
                            ) -> sut.SourceConstructor:
        return ConstructorOfStringSourceData(expected, unexpected)


class TestInvalidLineSequenceIsDetectedInDataBeforeFreeze(test_resources.TestInvalidLineSequenceIsDetectedBase):
    def _source_constructor(self,
                            valid: StringSourceData,
                            invalid: StringSourceData,
                            ) -> sut.SourceConstructor:
        return ConstructorOfStringSourceData(invalid, valid)


class TestInvalidLineSequenceIsDetectedInDataAfterFreeze(test_resources.TestInvalidLineSequenceIsDetectedBase):
    def _source_constructor(self,
                            valid: StringSourceData,
                            invalid: StringSourceData,
                            ) -> sut.SourceConstructor:
        return ConstructorOfStringSourceData(valid, invalid)


class TestExpectedHardErrorInContentsMethod(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        data_that_raises_hard_error_in_contents_methods = (
            StringSourceContentsData.new_w_defaults_of_hard_error(
                may_depend_on_external_resources=True
            )
        )

        source_constructor = _SourceConstructorForStringSourceOfContentsData(
            data_that_raises_hard_error_in_contents_methods,
            data_that_raises_hard_error_in_contents_methods,
        )

        expectation = sut.ExpectationOnUnFrozenAndFrozen.hard_error(
            asrt_text_doc.is_any_text(),
            may_depend_on_external_resources=asrt_str_src_contents.external_dependencies(),
        )

        for checker_variant in check_variants(expectation):
            with self.subTest(checker_variant=checker_variant.name):
                # ACT & ASSERT #
                checker_variant.value.apply_without_message(
                    self,
                    sut.SourceConstructors.of_common(source_constructor),
                )


class TestExpectedHardErrorExternalDependencies(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        def may_depend_on_external_resources() -> bool:
            raise HardErrorException(asrt_text_doc.new_single_string_text_for_test('hard err msg'))

        data_that_raises_hard_error_in_contents_methods = (
            StringSourceContentsData.of_constants_2(
                contents='',
                may_depend_on_external_resources=may_depend_on_external_resources
            )
        )

        source_constructor = _SourceConstructorForStringSourceOfContentsData(
            data_that_raises_hard_error_in_contents_methods,
            data_that_raises_hard_error_in_contents_methods,
        )

        expectation = sut.ExpectationOnUnFrozenAndFrozen(
            asrt_str_src_contents.Expectation(
                contents=asrt.anything_goes(),
                may_depend_on_external_resources=asrt_str_src_contents.ext_dependencies_raises_hard_error()
            ),
            frozen_may_depend_on_external_resources=asrt_str_src_contents.ext_dependencies_raises_hard_error(),
        )

        for checker_variant in check_variants(expectation):
            with self.subTest(checker_variant=checker_variant.name):
                # ACT & ASSERT #
                checker_variant.value.apply_without_message(
                    self,
                    sut.SourceConstructors.of_common(source_constructor),
                )


class TestUnexpectedHardErrorInContentsMethod(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        contents = 'the contents'
        data_that_raises_hard_error_in_contents_methods = (
            StringSourceContentsData.new_w_defaults_of_hard_error(
                may_depend_on_external_resources=True
            )
        )

        data_with_expected_data = StringSourceContentsData.of_constants(
            contents,
            may_depend_on_external_resources=True,
        )

        hex_before_or_after_freeze_cases = [
            NameAndValue(
                'before freeze',
                sut.SourceConstructors.of_common(
                    _SourceConstructorForStringSourceOfContentsData(
                        data_that_raises_hard_error_in_contents_methods,
                        data_with_expected_data,
                    )
                )
            ),
            NameAndValue(
                'after freeze',
                sut.SourceConstructors.of_common(
                    _SourceConstructorForStringSourceOfContentsData(
                        data_with_expected_data,
                        data_that_raises_hard_error_in_contents_methods,
                    )
                )
            ),
        ]

        expectation = sut.ExpectationOnUnFrozenAndFrozen.equals(
            contents,
            may_depend_on_external_resources=asrt.equals(asrt.anything_goes()),
            frozen_may_depend_on_external_resources=asrt.equals(asrt.anything_goes()),
        )

        for hex_before_or_after_freeze_case in hex_before_or_after_freeze_cases:
            for checker_variant in check_variants(expectation):
                with self.subTest(checker_variant=checker_variant.name,
                                  freeze_variant=hex_before_or_after_freeze_case.name):
                    # ACT & ASSERT #
                    test_utils.assert_that_assertion_fails(checker_variant.value,
                                                           hex_before_or_after_freeze_case.value)


class TestHardErrorShouldNeverHappenInFreeze(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        source_constructor = _SourceConstructorForStringWhoSFreezeRaisesHardError()

        expectation = sut.ExpectationOnUnFrozenAndFrozen.hard_error(
            asrt_text_doc.is_any_text(),
            may_depend_on_external_resources=asrt_str_src_contents.external_dependencies(),
        )

        for checker_variant in check_variants(expectation):
            with self.subTest(checker_variant=checker_variant.name):
                # ACT & ASSERT #
                test_utils.assert_that_assertion_fails(
                    checker_variant.value,
                    sut.SourceConstructors.of_common(source_constructor),
                )


class _SourceConstructorForStringSourceOfContentsData(SourceConstructorWAppEnvForTest):
    def __init__(self,
                 before_freeze: StringSourceContentsData,
                 after_freeze: StringSourceContentsData,
                 ):
        super().__init__()
        self._before_freeze = before_freeze
        self._after_freeze = after_freeze

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        def get_tmp_file_space() -> DirFileSpace:
            return app_env.tmp_files_space

        yield string_sources.StringSourceOfContents(
            self._before_freeze.as_contents(get_tmp_file_space),
            self._after_freeze.as_contents(get_tmp_file_space),
        )


class _SourceConstructorForStringWhoSFreezeRaisesHardError(SourceConstructorWAppEnvForTest):
    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        yield _StringSourceWhoSFreezeRaisesHardError()


class _StringSourceWhoSFreezeRaisesHardError(StringSourceTestImplBase):
    def __init__(self):
        super().__init__()
        self._contents = string_source_contents.ContentsThatRaisesHardErrorException()

    def contents(self) -> StringSourceContents:
        return self._contents

    def freeze(self):
        raise HardErrorException(
            asrt_text_doc.new_single_string_text_for_test('freeze not allowed here')
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
