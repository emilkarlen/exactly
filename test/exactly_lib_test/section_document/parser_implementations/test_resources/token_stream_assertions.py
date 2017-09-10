from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.util.parse.token import TokenType, Token
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def assert_token_stream(
        source: asrt.ValueAssertion = asrt.anything_goes(),
        remaining_source: asrt.ValueAssertion = asrt.anything_goes(),
        remaining_part_of_current_line: asrt.ValueAssertion = asrt.anything_goes(),
        remaining_source_after_head: asrt.ValueAssertion = asrt.anything_goes(),
        is_null: asrt.ValueAssertion = asrt.anything_goes(),
        head_token: asrt.ValueAssertion = asrt.anything_goes(),
        look_ahead_state: asrt.ValueAssertion = asrt.anything_goes(),
        position: asrt.ValueAssertion = asrt.anything_goes()) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        TokenStream,
        asrt.and_([
            asrt.sub_component('source', TokenStream.source.fget, source),
            asrt.sub_component('remaining_source',
                               TokenStream.remaining_source.fget,
                               remaining_source),
            asrt.sub_component('remaining_part_of_current_line',
                               TokenStream.remaining_part_of_current_line.fget,
                               remaining_part_of_current_line),
            asrt.sub_component('position', TokenStream.position.fget, position),
            asrt.sub_component('look_ahead_state', TokenStream.look_ahead_state.fget, look_ahead_state),
            asrt.sub_component('is_null', TokenStream.is_null.fget, is_null),
            asrt.or_([
                asrt.sub_component('is_null', TokenStream.is_null.fget, asrt.is_true),
                # The following must only be checked if not is_null (because of precondition):
                asrt.and_([
                    asrt.sub_component('head_token', TokenStream.head.fget, head_token),
                    asrt.sub_component('remaining_source_after_head',
                                       TokenStream.remaining_source_after_head.fget, remaining_source_after_head),
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
