from exactly_lib.section_document.parser_implementations.token_stream2 import TokenStream2
from exactly_lib.util.parse.token import TokenType, Token
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def assert_token_stream2(
        source: asrt.ValueAssertion = asrt.anything_goes(),
        remaining_source: asrt.ValueAssertion = asrt.anything_goes(),
        remaining_part_of_current_line: asrt.ValueAssertion = asrt.anything_goes(),
        remaining_source_after_head: asrt.ValueAssertion = asrt.anything_goes(),
        is_null: asrt.ValueAssertion = asrt.anything_goes(),
        head_token: asrt.ValueAssertion = asrt.anything_goes(),
        position: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        TokenStream2,
        asrt.and_([
            asrt.sub_component('source', TokenStream2.source.fget, source),
            asrt.sub_component('remaining_source',
                               TokenStream2.remaining_source.fget,
                               remaining_source),
            asrt.sub_component('remaining_part_of_current_line',
                               TokenStream2.remaining_part_of_current_line.fget,
                               remaining_part_of_current_line),
            asrt.sub_component('position', TokenStream2.position.fget, position),
            asrt.sub_component('is_null', TokenStream2.is_null.fget, is_null),
            asrt.or_([
                # The following must only be checked if not is_null (because of precondition of TokenStream2):
                asrt.sub_component('is_null', TokenStream2.is_null.fget, asrt.is_true),
                asrt.and_([
                    asrt.sub_component('head_token', TokenStream2.head.fget, head_token),
                    asrt.sub_component('remaining_source_after_head',
                                       TokenStream2.remaining_source_after_head.fget, remaining_source_after_head),
                ])
            ]),
        ]))


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


def assert_token_string_is(expected: str) -> asrt.ValueAssertion:
    return assert_token(string=asrt.equals(expected))


def assert_quoted(string: str,
                  source_string: str) -> asrt.ValueAssertion:
    return assert_token(token_type=asrt.equals(TokenType.QUOTED),
                        string=asrt.equals(string),
                        source_string=asrt.equals(source_string))


def assert_plain(string: str) -> asrt.ValueAssertion:
    return assert_token(token_type=asrt.equals(TokenType.PLAIN),
                        string=asrt.equals(string))
