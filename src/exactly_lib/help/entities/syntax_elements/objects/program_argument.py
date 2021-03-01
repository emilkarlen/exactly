from exactly_lib.common.help import headers
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, InvokationVariant
from exactly_lib.definitions import misc_texts, formatting, syntax_descriptions
from exactly_lib.definitions.argument_rendering import path_syntax
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, concepts, types
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation, \
    SyntaxElementDocumentation
from exactly_lib.impls.types.path import relative_path_options_documentation as rel_path_doc
from exactly_lib.impls.types.path.rel_opts_configuration import arg_config_with_name
from exactly_lib.impls.types.program import syntax_elements as pgm_syntax_elements
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser

TEXT_UNTIL_END_OF_LINE_ARGUMENT = a.Named('TEXT-UNTIL-END-OF-LINE')


def documentation() -> SyntaxElementDocumentation:
    invokation_variants = [
        _string(),
        _symbol_reference(),
        _text_until_end_of_line(),
        _existing_path(
            pgm_syntax_elements.EXISTING_FILE_OPTION_NAME,
            _EXISTING_FILE_DESCRIPTION,
        ),
        _existing_path(
            pgm_syntax_elements.EXISTING_DIR_OPTION_NAME,
            _EXISTING_DIR_DESCRIPTION,
        ),
        _existing_path(
            pgm_syntax_elements.EXISTING_PATH_OPTION_NAME,
            _EXISTING_PATH_DESCRIPTION,
        ),
    ]
    return syntax_element_documentation(
        None,
        syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT,
        _TEXT_PARSER.fnap(_MAIN__DESCRIPTION),
        (),
        invokation_variants,
        [
            rel_path_doc.path_element_2(
                PATH_OF_EXISTING_FILE_OPT_CONFIG,
                _TEXT_PARSER.paras(path_syntax.the_path_of_an_existing_file(final_dot=True)))

        ],
        cross_reference_id_list([
            syntax_elements.STRING_SYNTAX_ELEMENT,
            syntax_elements.PATH_SYNTAX_ELEMENT,
            syntax_elements.LIST_SYNTAX_ELEMENT,
            syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
        ]),
    )


def _existing_path(option: a.OptionName,
                   description_rest: str) -> InvokationVariant:
    return invokation_variant_from_args([
        a.Single(a.Multiplicity.MANDATORY,
                 a.Option(option)),
        a.Single(a.Multiplicity.MANDATORY,
                 PATH_OF_EXISTING_FILE_OPT_CONFIG.argument)
    ],
        _TEXT_PARSER.fnap(description_rest)
    )


def _text_until_end_of_line() -> InvokationVariant:
    return invokation_variant_from_args([
        a.Single(a.Multiplicity.MANDATORY,
                 a.Constant(pgm_syntax_elements.REMAINING_PART_OF_CURRENT_LINE_AS_LITERAL_MARKER)),
        a.Single(a.Multiplicity.MANDATORY,
                 TEXT_UNTIL_END_OF_LINE_ARGUMENT)
    ],
        _TEXT_PARSER.fnap(_TEXT_UNTIL_END_OF_LINE_DESCRIPTION)
    )


def _string() -> InvokationVariant:
    return invokation_variant_from_args([
        syntax_elements.STRING_SYNTAX_ELEMENT.single_mandatory,
    ],
    )


def _symbol_reference() -> InvokationVariant:
    return invokation_variant_from_args([
        syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.single_mandatory,
    ],
        _TEXT_PARSER.fnap(_SYMBOL_REFERENCE_DESCRIPTION)
    )


PATH_OF_EXISTING_FILE_OPT_CONFIG = arg_config_with_name('PATH-OF-EXISTING',
                                                        pgm_syntax_elements.EXE_FILE_REL_OPTION_ARG_CONF)

_TEXT_PARSER = TextParser({
    'string_type': types.STRING_TYPE_INFO.name,
    'string_se': formatting.syntax_element_(syntax_elements.STRING_SYNTAX_ELEMENT),
    'list_type': types.LIST_TYPE_INFO.name,
    'list_se': formatting.syntax_element_(syntax_elements.LIST_SYNTAX_ELEMENT),
    'path_type': types.PATH_TYPE_INFO.name,
    'path_se': formatting.syntax_element_(syntax_elements.PATH_SYNTAX_ELEMENT),
    'A_ref_to_symbol_w_string_conversion': types.a_ref_to_a_symbol_w_string_conversion__sentence(),
    'soft_quote': syntax_descriptions.SOFT_QUOTE_NAME,
    'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
    'SYMBOLIC_LINKS_ARE_FOLLOWED': misc_texts.SYMBOLIC_LINKS_ARE_FOLLOWED,
    'Note': headers.NOTE_LINE_HEADER,
    'Sym_refs_are_substituted': syntax_descriptions.symbols_are_substituted_in(
        TEXT_UNTIL_END_OF_LINE_ARGUMENT.name
    ),
})

_MAIN__DESCRIPTION = """\
An individual argument, or a list of arguments, in case of an unquoted reference
to {list_type:a/q} {symbol}.


An argument list is an ordinary {list_type:/q} value, with additional features
for text-until-end-of-line and references to existing files.
"""

_SYMBOL_REFERENCE_DESCRIPTION = """\
{A_ref_to_symbol_w_string_conversion}


{path_type:a/u} {symbol} gives a single argument that is its absolute path.


{list_type:a/u} {symbol} gives a list of arguments.


{Note} To pass a {list_type} as a single argument,
convert it to a {string_type} by surrounding it with {soft_quote:s}.
The elements will be separated by a single space.
"""

_TEXT_UNTIL_END_OF_LINE_DESCRIPTION = """\
The remaining part of the current line becomes a single argument.


{Sym_refs_are_substituted}
"""

_EXISTING_FILE_DESCRIPTION = """\
A {path_se}, with additional check for existence.


{SYMBOLIC_LINKS_ARE_FOLLOWED}.


Gives a single argument of an absolute path.
"""

_EXISTING_DIR_DESCRIPTION = """\
A {path_se}, with additional check for existence.


{SYMBOLIC_LINKS_ARE_FOLLOWED}.


Gives a single argument of an absolute path.
"""

_EXISTING_PATH_DESCRIPTION = """\
A {path_se}, with additional check for existence.


{SYMBOLIC_LINKS_ARE_FOLLOWED}.


Gives a single argument of an absolute path.
"""
