from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, SyntaxElementDescription
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.util.textformat.textformat_parser import TextParser

_EXPRESSION_DESCRIPTION = """\
An expression using Python syntax.


The expression must evaluate to an integer (a Python "int").
"""

_TEXT_PARSER = TextParser({
    'STRING': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
})

DOCUMENTATION = syntax_element_documentation(
    None,
    syntax_elements.INTEGER_SYNTAX_ELEMENT,
    (),
    (),
    [
        invokation_variant_from_args([
            syntax_elements.STRING_SYNTAX_ELEMENT.single_mandatory,
        ])
    ],
    [
        SyntaxElementDescription(
            syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
            _TEXT_PARSER.fnap(_EXPRESSION_DESCRIPTION),
        ),
    ],
    cross_reference_id_list([
        syntax_elements.STRING_SYNTAX_ELEMENT,
    ]))
