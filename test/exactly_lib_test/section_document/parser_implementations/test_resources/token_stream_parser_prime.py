from exactly_lib.section_document.parser_implementations.token_stream import TokenStream
from exactly_lib.section_document.parser_implementations.token_stream_parse_prime import TokenParserPrime


def remaining_source(remaining_contents_of_first_line: str,
                     following_lines: list = ()) -> TokenParserPrime:
    """
    :param remaining_contents_of_first_line: Part of the first line that has not been consumed.
    :return: Source with some initial content of the first line that has been consumed.
    """
    content = '\n'.join([remaining_contents_of_first_line] + list(following_lines))
    token_stream = TokenStream(content)
    return TokenParserPrime(token_stream)


def remaining_source_lines(lines: list) -> TokenParserPrime:
    """
    A variant of 'remaining_source'.
    """
    if not lines:
        raise ValueError('The source must contain at least one line')
    return remaining_source(lines[0], lines[1:])
