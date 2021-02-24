from exactly_lib.common.help.documentation_text import POSIX_SYNTAX
from exactly_lib.definitions import formatting
from exactly_lib.definitions.current_directory_and_path_type import path_type_path_rendering
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity import types, syntax_elements
from exactly_lib.definitions.formatting import InstructionName
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.entities.types.contents_structure import TypeDocumentation, TypeWithExpressionGrammarDocumentation
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser

_LIST_MAIN_DESCRIPTION_REST = """\
Used for argument lists, etc.
 
 
Useful when the {ATC} is a program with arguments,
and for the {run} instruction, e.g.
"""

_STRING_MAIN_DESCRIPTION_REST = """\
Used for arbitrary {string_type} values, and relative file names.
 
 
When used as a relative file name, {POSIX_SYNTAX} should be used.
"""

_TEXT_PARSER = TextParser({
    'run': InstructionName(instruction_names.RUN_INSTRUCTION_NAME),
    'POSIX_SYNTAX': POSIX_SYNTAX,
    'ATC': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
    'string_type': types.STRING_TYPE_INFO.name,
})

STRING_DOCUMENTATION = TypeDocumentation(types.STRING_TYPE_INFO,
                                         syntax_elements.STRING_SYNTAX_ELEMENT,
                                         _TEXT_PARSER.section_contents(_STRING_MAIN_DESCRIPTION_REST)
                                         )

LIST_DOCUMENTATION = TypeDocumentation(types.LIST_TYPE_INFO,
                                       syntax_elements.LIST_SYNTAX_ELEMENT,
                                       _TEXT_PARSER.section_contents(_LIST_MAIN_DESCRIPTION_REST)
                                       )

PATH_DOCUMENTATION = TypeDocumentation(types.PATH_TYPE_INFO,
                                       syntax_elements.PATH_SYNTAX_ELEMENT,
                                       SectionContents([],
                                                       [
                                                           path_type_path_rendering()
                                                       ]),
                                       [
                                           concepts.TCDS_CONCEPT_INFO.cross_reference_target,
                                       ]
                                       )
FILES_CONDITION_DOCUMENTATION = TypeWithExpressionGrammarDocumentation(
    types.FILES_CONDITION_TYPE_INFO,
    syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT)
