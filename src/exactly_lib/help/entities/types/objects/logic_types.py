from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.entity import types, syntax_elements, conf_params, concepts
from exactly_lib.help.entities.types.contents_structure import LogicTypeWithExpressionGrammarDocumentation, \
    TypeDocumentation
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.textformat.textformat_parser import TextParser

_TP = TextParser({
    'os_process': misc_texts.OS_PROCESS_NAME,
    'program_type': types.PROGRAM_TYPE_INFO.name,
    'conf_param': concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.name,
    'timeout_conf_param': formatting.conf_param_(conf_params.TIMEOUT_CONF_PARAM_INFO),
    'os_proc_env_section_header': misc_texts.OS_PROCESS_ENVIRONMENT_SECTION_HEADER,
    'test_case_spec_title': misc_texts.TEST_CASE_SPEC_TITLE,
    'current_OS': misc_texts.CURRENT_OS,
})

_LINE_MATCHER_DESCRIPTION = """\
The line separator depends on the {current_OS} ('\\n', '\\r\\n', e.g.).


Line separator are not included in the line contents.
"""

INTEGER_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.INTEGER_MATCHER_TYPE_INFO,
    syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT)

LINE_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.LINE_MATCHER_TYPE_INFO,
    syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT,
    _TP.section_contents(_LINE_MATCHER_DESCRIPTION))

FILE_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.FILE_MATCHER_TYPE_INFO,
    syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT)

FILES_CONDITION_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.FILES_CONDITION_TYPE_INFO,
    syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT)

STRING_TRANSFORMER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.STRING_TRANSFORMER_TYPE_INFO,
    syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT)

STRING_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.STRING_MATCHER_TYPE_INFO,
    syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT)

FILES_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.FILES_MATCHER_TYPE_INFO,
    syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT)

_PROGRAM_DESCRIPTION_REST = """\
{program_type:a/uq} is executed as an {os_process}.


The timeout of the {os_process} is determined by the {timeout_conf_param} {conf_param}.


The environment in which a {program_type} is executed
is described in "{test_case_spec_title}" / "{os_proc_env_section_header}".
"""

PROGRAM_DOCUMENTATION = TypeDocumentation(TypeCategory.LOGIC,
                                          types.PROGRAM_TYPE_INFO,
                                          syntax_elements.PROGRAM_SYNTAX_ELEMENT,
                                          _TP.section_contents(_PROGRAM_DESCRIPTION_REST),
                                          [
                                              conf_params.TIMEOUT_CONF_PARAM_INFO.cross_reference_target,
                                              PredefinedHelpContentsPartReference(
                                                  HelpPredefinedContentsPart.TEST_CASE_SPEC),
                                          ])
