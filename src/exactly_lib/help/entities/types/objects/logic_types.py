from exactly_lib.definitions import misc_texts, matcher_model
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.entity import types, syntax_elements, concepts
from exactly_lib.definitions.test_case import phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.entities.types.contents_structure import TypeWithExpressionGrammarDocumentation, \
    TypeDocumentation
from exactly_lib.type_val_prims.matcher import line_matcher
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser

_TP = TextParser({
    'os_process': misc_texts.OS_PROCESS_NAME,
    'program_type': types.PROGRAM_TYPE_INFO.name,
    'conf_param': concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.name,
    'os_proc_env_section_header': misc_texts.OS_PROCESS_ENVIRONMENT_SECTION_HEADER,
    'test_case_spec_title': misc_texts.TEST_CASE_SPEC_TITLE,
    'current_OS': misc_texts.CURRENT_OS,
    'First_line_number': line_matcher.FIRST_LINE_NUMBER_DESCRIPTION,
    'Line_separator_description': line_matcher.LINE_SEPARATOR_DESCRIPTION,
    'text_model': matcher_model.TEXT_MODEL,
    'string_source_type': types.STRING_SOURCE_TYPE_INFO.name,
})

_LINE_MATCHER_DESCRIPTION = """\
A line is represented by its


  * line number
  * text contents


{First_line_number}


The line separator is not included in the text contents.


{Line_separator_description}
"""

INTEGER_MATCHER_DOCUMENTATION = TypeWithExpressionGrammarDocumentation(
    types.INTEGER_MATCHER_TYPE_INFO,
    syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT)

LINE_MATCHER_DOCUMENTATION = TypeWithExpressionGrammarDocumentation(
    types.LINE_MATCHER_TYPE_INFO,
    syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT,
    _TP.section_contents(_LINE_MATCHER_DESCRIPTION))

FILE_MATCHER_DOCUMENTATION = TypeWithExpressionGrammarDocumentation(
    types.FILE_MATCHER_TYPE_INFO,
    syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT)

STRING_TRANSFORMER_DOCUMENTATION = TypeWithExpressionGrammarDocumentation(
    types.STRING_TRANSFORMER_TYPE_INFO,
    syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT,
    SectionContents.empty(),
    ())

STRING_MATCHER_DOCUMENTATION = TypeWithExpressionGrammarDocumentation(
    types.STRING_MATCHER_TYPE_INFO,
    syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
    SectionContents.empty(),
    ())

FILES_MATCHER_DOCUMENTATION = TypeWithExpressionGrammarDocumentation(
    types.FILES_MATCHER_TYPE_INFO,
    syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT)

_PROGRAM_DESCRIPTION_REST = """\
{program_type:a/uq} is executed as an {os_process}.


The environment in which a {program_type} is executed
is described in "{test_case_spec_title}" / "{os_proc_env_section_header}".
"""

PROGRAM_DOCUMENTATION = TypeDocumentation(
    types.PROGRAM_TYPE_INFO,
    syntax_elements.PROGRAM_SYNTAX_ELEMENT,
    _TP.section_contents(_PROGRAM_DESCRIPTION_REST),
    [
        PredefinedHelpContentsPartReference(
            HelpPredefinedContentsPart.TEST_CASE_SPEC),
        phase_infos.SETUP.instruction_cross_reference_target(instruction_names.ENV_VAR_INSTRUCTION_NAME),
        phase_infos.SETUP.instruction_cross_reference_target(instruction_names.TIMEOUT_INSTRUCTION_NAME),
    ])

_STRING_SOURCE_DESCRIPTION_REST = """\
Produces {text_model:a}, when referenced.


The produced {text_model} may differ when {string_source_type:a/q}
is referenced from different locations.

One such example is {string_source_type:a/q} that is
the output from {program_type:a/q}
that produces different output on different
executions.
"""

STRING_SOURCE_DOCUMENTATION = TypeDocumentation(
    types.STRING_SOURCE_TYPE_INFO,
    syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT,
    _TP.section_contents(_STRING_SOURCE_DESCRIPTION_REST),
)
