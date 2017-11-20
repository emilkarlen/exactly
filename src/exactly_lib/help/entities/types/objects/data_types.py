from exactly_lib.help.entities.types.contents_structure import TypeDocumentation
from exactly_lib.help_texts.entity import types, syntax_element
from exactly_lib.help_texts.names.formatting import InstructionName
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.textformat.structure.document import empty_contents
from exactly_lib.util.textformat.textformat_parser import TextParser

_LIST_MAIN_DESCRIPTION_REST = """\
Used for argument lists.
 
 
Useful when the SUT is a command line program,
and for the {run} instruction, e.g.
"""

_TEXT_PARSER = TextParser({
    'run': InstructionName(instruction_names.RUN_INSTRUCTION_NAME),
})

STRING_DOCUMENTATION = TypeDocumentation(TypeCategory.DATA,
                                         types.STRING_TYPE_INFO,
                                         syntax_element.STRING_SYNTAX_ELEMENT,
                                         empty_contents())

LIST_DOCUMENTATION = TypeDocumentation(TypeCategory.DATA,
                                       types.LIST_TYPE_INFO,
                                       syntax_element.LIST_SYNTAX_ELEMENT,
                                       _TEXT_PARSER.section_contents(_LIST_MAIN_DESCRIPTION_REST))

PATH_DOCUMENTATION = TypeDocumentation(TypeCategory.DATA,
                                       types.PATH_TYPE_INFO,
                                       syntax_element.PATH_SYNTAX_ELEMENT,
                                       empty_contents())
