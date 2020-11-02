from typing import Sequence

from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args
from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.argument_rendering import path_syntax
from exactly_lib.definitions.cross_ref import name_and_cross_ref
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.help.entities.syntax_elements.contents_structure import syntax_element_documentation, \
    SyntaxElementDocumentation
from exactly_lib.help.entities.utils import programs
from exactly_lib.impls.actors.util import parse_act_interpreter
from exactly_lib.impls.types.path import relative_path_options_documentation as rel_path_doc
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def documentation() -> SyntaxElementDocumentation:
    executable_arg = syntax_elements.PATH_SYNTAX_ELEMENT.single_mandatory
    optional_arguments_arg = syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT.zero_or_more

    invokation_variants = [
        invokation_variant_from_args([executable_arg,
                                      optional_arguments_arg],
                                     _executable_file_description()),
        programs.system_program([optional_arguments_arg]),
        programs.python_interpreter([optional_arguments_arg]),
    ]
    return syntax_element_documentation(
        None,
        syntax_elements.ACT_INTERPRETER_SYNTAX_ELEMENT,
        _TEXT_PARSER.fnap(_MAIN__DESCRIPTION),
        (),
        invokation_variants,
        [],
        name_and_cross_ref.cross_reference_id_list([
            syntax_elements.PATH_SYNTAX_ELEMENT,
            syntax_elements.STRING_SYNTAX_ELEMENT,
            syntax_elements.PROGRAM_ARGUMENT_SYNTAX_ELEMENT,
        ]),
    )


def _executable_file_description() -> Sequence[ParagraphItem]:
    return rel_path_doc.path_element_relativity_paragraphs(
        parse_act_interpreter.EXE_FILE_RELATIVITIES.options,
        _TEXT_PARSER.paras(path_syntax.the_path_of('{executable_file:a}.')),
    )


_TEXT_PARSER = TextParser({
    'executable_file': formatting.misc_name_with_formatting(misc_texts.EXECUTABLE_FILE),
    'external_program': misc_texts.EXTERNAL_PROGRAM,
    'PATH': syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
    'symbol': concepts.SYMBOL_CONCEPT_INFO.name,
    'setup_phase': phase_names.SETUP,
})

_MAIN__DESCRIPTION = """\
{external_program:a/u} that interprets a source code file, who's path is given as a command line argument.


When the program is applied, the path of the source code file is added as the last argument.


Referenced {symbol:s} must have been defined in the {setup_phase:emphasis} phase.
"""
