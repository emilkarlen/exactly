from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.entity import types, syntax_elements, conf_params, concepts
from exactly_lib.help.entities.types.contents_structure import LogicTypeWithExpressionGrammarDocumentation, \
    TypeDocumentation
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_condition import parse as parse_files_condition
from exactly_lib.test_case_utils.files_matcher import parse_files_matcher
from exactly_lib.test_case_utils.line_matcher import parse_line_matcher
from exactly_lib.test_case_utils.string_matcher import parse_string_matcher
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.textformat.structure.document import empty_section_contents
from exactly_lib.util.textformat.textformat_parser import TextParser

_TP = TextParser({
    'os_process': misc_texts.OS_PROCESS_NAME,
    'program_type': types.PROGRAM_TYPE_INFO.name,
    'conf_param': concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.name,
    'timeout_conf_param': formatting.conf_param_(conf_params.TIMEOUT_CONF_PARAM_INFO),
    'os_proc_env_section_header': misc_texts.OS_PROCESS_ENVIRONMENT_SECTION_HEADER,
    'test_case_spec_title': misc_texts.TEST_CASE_SPEC_TITLE,
})

LINE_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.LINE_MATCHER_TYPE_INFO,
    syntax_elements.LINE_MATCHER_SYNTAX_ELEMENT,
    parse_line_matcher.GRAMMAR,
    empty_section_contents())

FILE_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.FILE_MATCHER_TYPE_INFO,
    syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT,
    parse_file_matcher.GRAMMAR,
    empty_section_contents())

FILES_CONDITION_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.FILES_CONDITION_TYPE_INFO,
    syntax_elements.FILES_CONDITION_SYNTAX_ELEMENT,
    parse_files_condition.GRAMMAR,
    empty_section_contents())

STRING_TRANSFORMER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.STRING_TRANSFORMER_TYPE_INFO,
    syntax_elements.STRING_TRANSFORMER_SYNTAX_ELEMENT,
    parse_string_transformer.GRAMMAR,
    empty_section_contents())

STRING_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.STRING_MATCHER_TYPE_INFO,
    syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT,
    parse_string_matcher.GRAMMAR,
    empty_section_contents())

FILES_MATCHER_DOCUMENTATION = LogicTypeWithExpressionGrammarDocumentation(
    types.FILES_MATCHER_TYPE_INFO,
    syntax_elements.FILES_MATCHER_SYNTAX_ELEMENT,
    parse_files_matcher.GRAMMAR,
    empty_section_contents())

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
