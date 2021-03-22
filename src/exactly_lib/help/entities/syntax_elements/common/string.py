from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, InvokationVariant
from exactly_lib.definitions import syntax_descriptions, misc_texts, formatting
from exactly_lib.impls.types.program import syntax_elements as pgm_syntax_elements
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

TEXT_UNTIL_END_OF_LINE_ARGUMENT = a.Named('TEXT-UNTIL-END-OF-LINE')


def text_until_end_of_line() -> InvokationVariant:
    return invokation_variant_from_args([
        a.Single(a.Multiplicity.MANDATORY,
                 a.Constant(pgm_syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER)),
        a.Single(a.Multiplicity.MANDATORY,
                 TEXT_UNTIL_END_OF_LINE_ARGUMENT)
    ],
        _TEXT_PARSER.fnap(_TEXT_UNTIL_END_OF_LINE_DESCRIPTION)
    )


_TEXT_PARSER = TextParser({
    'Sym_refs_are_substituted': syntax_descriptions.symbols_are_substituted_in(
        TEXT_UNTIL_END_OF_LINE_ARGUMENT.name
    ),
    'White_pace': misc_texts.WHITESPACE.capitalize(),
    'token': formatting.keyword(pgm_syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER),
})

_TEXT_UNTIL_END_OF_LINE_DESCRIPTION = """\
The text after {token} until the end of the line becomes a single string.


{White_pace} at both ends is removed.


{Sym_refs_are_substituted}
"""
