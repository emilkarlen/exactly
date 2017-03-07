from exactly_lib.section_document.parser_implementations.token import TokenType, Token
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def assert_token(token_type: asrt.ValueAssertion = asrt.anything_goes(),
                 string: asrt.ValueAssertion = asrt.anything_goes(),
                 source_string: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
    return asrt.And([
        asrt.is_instance(Token, 'Value to apply assertions on must be a {}'.format(
            Token)),
        asrt.sub_component('type', Token.type.fget, token_type),
        asrt.sub_component('string', Token.string.fget, string),
        asrt.sub_component('source_string', Token.source_string.fget, source_string),
    ])


def assert_quoted(string: str,
                  source_string: str) -> asrt.ValueAssertion:
    return assert_token(token_type=asrt.equals(TokenType.QUOTED),
                        string=asrt.equals(string),
                        source_string=asrt.equals(source_string))


def assert_plain(string: str) -> asrt.ValueAssertion:
    return assert_token(token_type=asrt.equals(TokenType.PLAIN),
                        string=asrt.equals(string))
