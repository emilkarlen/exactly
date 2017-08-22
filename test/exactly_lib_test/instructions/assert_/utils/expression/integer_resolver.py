import unittest

from exactly_lib.instructions.assert_.utils.expression import integer_resolver as sut
from exactly_lib.instructions.utils.return_svh_via_exceptions import SvhValidationException
from exactly_lib.named_element.symbol import string_resolver
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils
from exactly_lib_test.named_element.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case.test_resources import instruction_environment
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_hds, fake_sds
from exactly_lib_test.test_resources.actions import do_return


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValidationPreSds),
        unittest.makeSuite(TestValidateAndResolve),
    ])


class TestValidateAndResolve(unittest.TestCase):
    def test(self):
        # ARRANGE #

        symbol_simple = Symbol('symbol_simple', 3, '3')

        symbol_complex = Symbol('symbol_complex', 7, '2 + 5')

        defined_symbols = self._symbol_table_with_string_values([
            symbol_simple,
            symbol_complex,
        ])

        the_instruction_environment = InstructionEnvironmentForPostSdsStep(
            hds=fake_hds(),
            environ={},
            sds=fake_sds(),
            phase_identifier='ignored phase identifier',
            symbols=defined_symbols,
        )

        cases = [
            Case(
                'single constant integer',
                '1',
                Expected(
                    resolved_value=1,
                    symbol_references=[])
            ),
            Case(
                'single symbol reference with simple contents',
                symbol_simple.ref_syntax,
                Expected(
                    resolved_value=symbol_simple.value_int,
                    symbol_references=[symbol_simple.symbol_reference]
                )),
            Case(
                'constant complex expression',
                '1 + 2*3 * (2+2)',
                Expected(
                    resolved_value=1 + 2 * 3 * (2 + 2),
                    symbol_references=[])
            ),
            Case(
                'single symbol reference with complex contents',
                symbol_complex.ref_syntax,
                Expected(
                    resolved_value=symbol_complex.value_int,
                    symbol_references=[symbol_complex.symbol_reference]
                )
            ),
            Case(
                'mixed expression',
                '1 + {symbol_simple} * ({symbol_complex})'.format(
                    symbol_simple=symbol_simple.ref_syntax,
                    symbol_complex=symbol_complex.ref_syntax),
                Expected(
                    resolved_value=1 + symbol_simple.value_int * symbol_complex.value_int,
                    symbol_references=[symbol_simple.symbol_reference,
                                       symbol_complex.symbol_reference]
                )
            ),
        ]
        for case in cases:
            with self.subTest(case_name=case.name, source_str=case.source,
                              expected_value=case.expected.resolved_value):
                # ARRANGE #

                string_value_resolver = parse_string.string_resolver_from_string(case.source)
                resolver_to_check = sut.IntegerResolver('prop to check', string_value_resolver)

                # ACT #

                actual_symbol_references = resolver_to_check.references

                resolver_to_check.validate_pre_sds(the_instruction_environment)

                actual = resolver_to_check.resolve(the_instruction_environment)

                # ASSERT #

                self.assertEqual(case.expected.resolved_value,
                                 actual)

                equals_symbol_references(case.expected.symbol_references).apply_without_message(self,
                                                                                                actual_symbol_references)

    def _symbol_table_with_string_values(self, all_symbols):
        return SymbolTable(
            dict([(sym.name, symbol_utils.string_value_constant_container(sym.value_str))
                  for sym in all_symbols]))


class TestSymbolReferences(unittest.TestCase):
    def test_no_references_SHOULD_be_reported_WHEN_string_resolver_has_no_references(self):
        # ARRANGE #

        resolver_to_check = sut.IntegerResolver(
            'the property to check',
            string_resolver.string_constant(str(1)))

        # ACT #

        actual = resolver_to_check.references

        # ASSERT #

        self.assertEqual([], actual,
                         'no references should be reported')

    def test_references_of_string_resolver_SHOULD_be_reported(self):
        # ARRANGE #

        reference_of_string_resolver = symbol_utils.symbol_reference('symbol name')

        the_string_resolver = string_resolver.symbol_reference(reference_of_string_resolver)

        resolver_to_check = sut.IntegerResolver(
            'the property to check',
            the_string_resolver)

        # ACT #

        actual = resolver_to_check.references

        # ASSERT #

        expected_references = [reference_of_string_resolver]

        assertion = equals_symbol_references(expected_references)

        assertion.apply_without_message(self, actual)


class TestValidationPreSds(unittest.TestCase):
    def test_validation_SHOULD_fail_WHEN_resolved_value_is_not_an_integer(self):

        the_instruction_environment = instruction_environment.fake_pre_sds_environment()
        test_cases = [
            'a',
            '1+x',
            'a b',
            '10 a',
            '10a',
            '1.5',
        ]
        for custom_validator in [None, do_return(None)]:
            for resolved_value in test_cases:
                with self.subTest(
                        custom_validator_is_none=str(custom_validator is None),
                        resolved_value=resolved_value):
                    # ARRANGE #
                    resolver_to_check = sut.IntegerResolver('the property to check',
                                                            string_resolver.string_constant(resolved_value),
                                                            custom_validator)
                    # ACT & ASSERT #
                    with self.assertRaises(SvhValidationException) as cm:
                        resolver_to_check.validate_pre_sds(the_instruction_environment)

                    self.assertIsInstance(cm.exception.err_msg,
                                          str,
                                          'the error message should be a str')

    def test_validation_SHOULD_fail_WHEN_custom_validator_fails(self):

        the_instruction_environment = instruction_environment.fake_pre_sds_environment()

        resolved_value = 1

        # ARRANGE #
        error_message_from_custom_validator = 'error message'
        resolver_to_check = sut.IntegerResolver(
            'the property to check',
            string_resolver.string_constant(str(resolved_value)),
            CustomValidator(value_that_makes_the_validation_succeed=resolved_value + 1,
                            error_message=error_message_from_custom_validator))
        # ACT & ASSERT #
        with self.assertRaises(SvhValidationException) as cm:
            resolver_to_check.validate_pre_sds(the_instruction_environment)

        self.assertEqual(error_message_from_custom_validator,
                         cm.exception.err_msg)

    def test_validation_SHOULD_succeed_WHEN_value_is_an_integer_and_custom_validator_succeeds(self):

        the_instruction_environment = instruction_environment.fake_pre_sds_environment()

        resolved_value = 16

        resolved_string_value_cases = [
            '16',
            '8 + 8',
            '2 * 2 * 2 * 2',
        ]

        custom_validator_cases = [
            None,
            CustomValidator(value_that_makes_the_validation_succeed=resolved_value,
                            error_message='error message from custom validator')
        ]
        for value_string in resolved_string_value_cases:
            for custom_validator in custom_validator_cases:
                resolver_to_check = sut.IntegerResolver(
                    'the property to check',
                    string_resolver.string_constant(str(value_string)),
                    custom_validator)
                with self.subTest(custom_validator_is_none=str(custom_validator is None),
                                  value_string=value_string):
                    resolver_to_check.validate_pre_sds(the_instruction_environment)


class CustomValidator:
    def __init__(self, value_that_makes_the_validation_succeed: int,
                 error_message: str):
        self.error_message = error_message
        self.value_that_makes_the_validation_succeed = value_that_makes_the_validation_succeed

    def __call__(self, value: int):
        if value != self.value_that_makes_the_validation_succeed:
            return self.error_message

        return None


class Expected:
    def __init__(self,
                 resolved_value: int,
                 symbol_references: list):
        self.resolved_value = resolved_value
        self.symbol_references = symbol_references


class Case:
    def __init__(self,
                 name: str,
                 source: str,
                 expected: Expected):
        self.name = name
        self.source = source
        self.expected = expected


class Symbol:
    def __init__(self,
                 name: str,
                 value_int: int,
                 value_str: str,
                 ):
        self.name = name
        self.value_int = value_int
        self.value_str = value_str
        self.ref_syntax = symbol_reference_syntax_for_name(name)
        self.symbol_reference = symbol_utils.symbol_reference(name)
