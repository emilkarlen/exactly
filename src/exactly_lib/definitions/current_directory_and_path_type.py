from typing import List

from exactly_lib.common.help import headers
from exactly_lib.common.help.documentation_text import paths_uses_posix_syntax
from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions import path
from exactly_lib.definitions.entity import concepts, types
from exactly_lib.definitions.formatting import InstructionName
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionItem, Section
from exactly_lib.util.textformat.textformat_parser import TextParser


def abs_or_rel_path_of_existing(file_type: str,
                                syntax_element: str,
                                relativity_root: str) -> List[ParagraphItem]:
    tp = TextParser({
        'file_type': file_type,
        'syntax_element': syntax_element,
        'relativity_root': relativity_root
    })
    return tp.fnap(_PATH_DESCRIPTION) + paths_uses_posix_syntax()


_PATH_DESCRIPTION = """\
The absolute or relative path of an existing {file_type}.


If {syntax_element} is relative, then it's relative to the {relativity_root}.
"""


def def_instruction_rel_cd_description(path_arg_name: str) -> List[ParagraphItem]:
    tp = TextParser({
        'current_directory_concept': formatting.concept_(
            concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
        'path_arg': path_arg_name,
        'symbol_concept': formatting.concept(concepts.SYMBOL_CONCEPT_INFO.singular_name),
        'symbols_concept': formatting.concept(concepts.SYMBOL_CONCEPT_INFO.plural_name),
        'Note': headers.NOTE_LINE_HEADER,
    })
    return tp.fnap(_DEF_INSTRUCTION_REL_CD_DESCRIPTION)


def cd_instruction_section_on_def_instruction() -> List[ParagraphItem]:
    tp = TextParser({
        'current_directory_concept': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
        'def_instruction': InstructionName(instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME),
        'symbol_concept': formatting.concept(concepts.SYMBOL_CONCEPT_INFO.singular_name),
        'rel_cd_option': formatting.cli_option(path.REL_CWD_OPTION),
        'path_type': types.PATH_TYPE_INFO.name,
    })
    return tp.fnap(_CD_INSTRUCTION_SECTION_ON_DEF_INSTRUCTION)


def path_type_path_rendering() -> SectionItem:
    tp = TextParser({
        'current_directory_concept': formatting.concept_(concepts.CURRENT_WORKING_DIRECTORY_CONCEPT_INFO),
        'def_instruction': InstructionName(instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME),
        'symbol_concept': formatting.concept(concepts.SYMBOL_CONCEPT_INFO.singular_name),
        'rel_cd_option': formatting.cli_option(path.REL_CWD_OPTION),
        'path_type': types.PATH_TYPE_INFO.name,
        'external_program': misc_texts.EXTERNAL_PROGRAM,
        'os_process': misc_texts.OS_PROCESS_NAME,
        'Note': headers.NOTE_LINE_HEADER,
    })
    return Section(tp.text(_PATH_TYPE_PATH_RENDERING_DESCRIPTION_HEADER),
                   tp.section_contents(_PATH_TYPE_PATH_RENDERING_DESCRIPTION))


_CD_INSTRUCTION_SECTION_ON_DEF_INSTRUCTION = """\
The {def_instruction} is special because a {symbol_concept} definition is
evaluated each time it is referenced - not when it is defined
(i.e. not when the {def_instruction} instruction is executed).


This means, that when a {path_type} {symbol_concept} is defined
with a relativity of {current_directory_concept}
({rel_cd_option})
it is relative the directory that is current when the symbol is REFERENCED,

not when it is defined.
"""

_DEF_INSTRUCTION_REL_CD_DESCRIPTION = """\
{Note} When a {path_arg} value is defined to be relative the {current_directory_concept},
it means that it is relative the directory that is current when the symbol is REFERENCED,

not when it is defined.
"""

_PATH_TYPE_PATH_RENDERING_DESCRIPTION_HEADER = 'Rendering of {path_type} values'

_PATH_TYPE_PATH_RENDERING_DESCRIPTION = """\
All {path_type} values are rendered as absolute paths.


This means, e.g., that values can be passed to {external_program:s},
which may use them without consideration of the current directory of the {os_process}.


{Note} {path_type:a/u} value that is defined using the {def_instruction} instruction
with relativity of {current_directory_concept}
({rel_cd_option}) is evaluated when it is REFERENCED,
not when it is defined.


This means that the rendered value is different if it is referenced in
different locations with different {current_directory_concept}.
"""
