from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation
from exactly_lib.util.textformat.textformat_parser import TextParser

_MAIN_DESCRIPTION_REST = """\
A {SYNTAX_ELEMENT} is passed as a single string to the operating system's shell,
so all features of the shell can be used.


Any {SYMBOL_REFERENCE_SYNTAX_ELEMENT} appearing in the string is substituted.


Us of the shell is of course not portable since it
depends on the current operating system environment's shell.


On POSIX, the shell defaults to /bin/sh.

On Windows, the COMSPEC environment variable specifies the default shell.
"""

_TEXT_PARSER = TextParser({
    'SYMBOL_REFERENCE_SYNTAX_ELEMENT': syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT.singular_name,
    'SYNTAX_ELEMENT': formatting.syntax_element_(syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT)

})
DOCUMENTATION = syntax_element_documentation(None,
                                             syntax_elements.SHELL_COMMAND_LINE_SYNTAX_ELEMENT,
                                             _TEXT_PARSER.fnap(_MAIN_DESCRIPTION_REST),
                                             [],
                                             [],
                                             cross_reference_id_list([
                                                 syntax_elements.SYMBOL_REFERENCE_SYNTAX_ELEMENT,
                                             ]))
