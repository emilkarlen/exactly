from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name

_MAIN_DESCRIPTION_REST = symbol_reference_syntax_for_name(syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument.name)

DOCUMENTATION = syntax_element_documentation(
    None,
    syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
    [],
    [
        InvokationVariant(
            symbol_reference_syntax_for_name(syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT.argument.name)
        )

    ],
    [],
    cross_reference_id_list([
        concepts.SYMBOL_CONCEPT_INFO,
        syntax_elements.SYMBOL_NAME_SYNTAX_ELEMENT,
    ]))
