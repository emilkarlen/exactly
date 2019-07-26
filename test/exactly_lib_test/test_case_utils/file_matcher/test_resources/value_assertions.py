import unittest
from typing import Set

from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.file_matcher.impl.file_type import FileMatcherType
from exactly_lib.test_case_utils.file_matcher.impl.name_glob_pattern import FileMatcherNameGlobPattern
from exactly_lib.test_case_utils.file_matcher.impl.name_regex import FileMatcherBaseNameRegExPattern
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherValue
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_case_utils.file_matcher.test_resources.visitor import FileMatcherStructureVisitor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def equals_file_matcher(expected: FileMatcher,
                        description: str = '') -> ValueAssertion[FileMatcher]:
    return _EqualsAssertion(expected, description)


def value_equals_file_matcher(expected: FileMatcher,
                              description: str = '') -> ValueAssertion[FileMatcherValue]:
    return _EqualsAssertionValue(expected, description)


def matches_file_matcher_value(
        primitive_value: ValueAssertion[FileMatcher] = asrt.anything_goes(),
        resolving_dependencies: ValueAssertion[Set[DirectoryStructurePartition]] = asrt.anything_goes(),
        validator: ValueAssertion[PreOrPostSdsValueValidator] = asrt.anything_goes(),
        tcds: HomeAndSds = fake_home_and_sds(),
) -> ValueAssertion[FileMatcherValue]:
    def resolve_primitive_value(value: FileMatcherValue):
        return value.value_of_any_dependency(tcds)

    def get_resolving_dependencies(value: FileMatcherValue):
        return value.resolving_dependencies()

    def get_validator(value: FileMatcherValue):
        return value.validator()

    return asrt.is_instance_with__many(
        FileMatcherValue,
        [
            asrt.sub_component_many(
                'resolving dependencies',
                get_resolving_dependencies,
                [
                    asrt.is_set_of(asrt.is_instance(DirectoryStructurePartition)),
                    resolving_dependencies,
                ]
            ),
            asrt.sub_component(
                'primitive value',
                resolve_primitive_value,
                asrt.is_instance_with(FileMatcher,
                                      primitive_value)
            ),
            asrt.sub_component(
                'validator',
                get_validator,
                asrt.is_instance_with(PreOrPostSdsValueValidator,
                                      validator)
            ),
        ]
    )


class _EqualsAssertion(ValueAssertionBase[FileMatcher]):
    def __init__(self,
                 expected: FileMatcher,
                 description: str):
        self.expected = expected
        self.description = description

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        assert_is_file_selector_type = asrt.is_instance(FileMatcher, self.description)
        assert_is_file_selector_type.apply_with_message(put, value,
                                                        'Value must be a ' + str(FileMatcher))
        checker = _StructureChecker(put,
                                    message_builder,
                                    self.expected,
                                    self.description
                                    )
        checker.visit(value)


class _EqualsAssertionValue(ValueAssertionBase[FileMatcherValue]):
    TCDS = fake_home_and_sds()

    def __init__(self,
                 expected: FileMatcher,
                 description: str):
        self.expected = expected
        self.description = description

    def _apply(self,
               put: unittest.TestCase,
               actual,
               message_builder: asrt.MessageBuilder):
        assert_is_file_selector_type = asrt.is_instance(FileMatcherValue, self.description)
        assert_is_file_selector_type.apply_with_message(put, actual,
                                                        'Value must be a ' + str(FileMatcherValue))
        assert isinstance(actual, FileMatcherValue)

        assertion_on_primitive_value = equals_file_matcher(self.expected, self.description)
        assertion_on_primitive_value.apply(put,
                                           actual.value_of_any_dependency(self.TCDS),
                                           message_builder)


class _StructureChecker(FileMatcherStructureVisitor):
    def __init__(self,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder,
                 expected: FileMatcher,
                 description: str):
        self.put = put
        self.message_builder = message_builder
        self.expected = expected
        self.description = description

    def _common(self, actual: file_matchers.FileMatcher):
        self.put.assertIsInstance(actual,
                                  type(self.expected),
                                  'class')
        self.put.assertEqual(actual.option_description,
                             self.expected.option_description,
                             'option_description')

    def visit_name_glob_pattern(self, actual: FileMatcherNameGlobPattern):
        self._common(actual)
        assert isinstance(self.expected, FileMatcherNameGlobPattern)  # Type info for IDE
        self.put.assertEqual(self.expected.glob_pattern,
                             actual.glob_pattern,
                             'glob_pattern')

    def visit_name_reg_ex_pattern(self, actual: FileMatcherBaseNameRegExPattern):
        self._common(actual)
        assert isinstance(self.expected, FileMatcherBaseNameRegExPattern)  # Type info for IDE
        self.put.assertEqual(self.expected.reg_ex_pattern,
                             actual.reg_ex_pattern,
                             'reg_ex_pattern')

    def visit_constant(self, actual: file_matchers.FileMatcherConstant):
        self._common(actual)
        assert isinstance(self.expected, file_matchers.FileMatcherConstant)  # Type info for IDE
        self.put.assertEqual(self.expected.result_constant,
                             actual.result_constant,
                             'result_constant')

    def visit_type(self, actual: FileMatcherType):
        self._common(actual)
        assert isinstance(self.expected, FileMatcherType)  # Type info for IDE
        self.put.assertEqual(self.expected.file_type,
                             actual.file_type,
                             'file_type')

    def visit_not(self, actual: file_matchers.FileMatcherNot):
        self._common(actual)
        assert isinstance(self.expected, file_matchers.FileMatcherNot)  # Type info for IDE
        assertion_on_negated_matchers = equals_file_matcher(self.expected.negated_matcher)
        assertion_on_negated_matchers.apply_with_message(self.put, actual.negated_matcher,
                                                         'negated matcher')

    def visit_and(self, actual: file_matchers.FileMatcherAnd):
        self._common(actual)
        assert isinstance(self.expected, file_matchers.FileMatcherAnd)  # Type info for IDE
        assertion_on_sub_matchers = asrt.matches_sequence(list(map(equals_file_matcher, self.expected.matchers)))
        assertion_on_sub_matchers.apply_with_message(self.put, actual.matchers,
                                                     'sub matchers')

    def visit_or(self, actual: file_matchers.FileMatcherOr):
        self._common(actual)
        assert isinstance(self.expected, file_matchers.FileMatcherOr)  # Type info for IDE
        assertion_on_sub_matchers = asrt.matches_sequence(list(map(equals_file_matcher, self.expected.matchers)))
        assertion_on_sub_matchers.apply_with_message(self.put, actual.matchers,
                                                     'sub matchers')
