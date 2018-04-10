from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.util.textformat.textformat_parser import TextParser

_MAIN_DESCRIPTION_REST = """\
A {STRING} that is an expression that evaluates to an integer (using Python syntax).


May be quoted (to allow space).


{SYMBOL_REFERENCE_SYNTAX_ELEMENT}s are substituted.
"""

_TEXT_PARSER = TextParser({
    'STRING': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
    'SYMBOL_REFERENCE_SYNTAX_ELEMENT': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name

})
DOCUMENTATION = syntax_element_documentation(None,
                                             syntax_elements.INTEGER_SYNTAX_ELEMENT,
                                             _TEXT_PARSER.fnap(_MAIN_DESCRIPTION_REST),
                                             [],
                                             [],
                                             cross_reference_id_list([
                                                 syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
                                                 syntax_elements.STRING_SYNTAX_ELEMENT,
                                             ]))
