from exactly_lib import program_info
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help_texts import test_case_file_structure as tc_fs, formatting
from exactly_lib.help_texts.cross_ref.concrete_cross_refs import TestCasePhaseInstructionCrossReference
from exactly_lib.help_texts.doc_format import instruction_name_text
from exactly_lib.help_texts.entity import concepts, conf_params, syntax_elements
from exactly_lib.help_texts.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.help_texts.test_case import phase_names
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.lists import HeaderContentListItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class _DirInfo:
    def __init__(self,
                 relativity_option_type: RelHomeOptionType,
                 dir_info: tc_fs.TcDirInfo,
                 conf_param: ConfigurationParameterInfo,
                 instruction_name: str,
                 ):
        self.conf_param = conf_param
        self.relativity_option_type = relativity_option_type
        self.default_value_description = conf_param.default_value_single_line_description
        self.conf_param = conf_param
        self.dir_info = dir_info
        self.item_name = self.dir_info.informative_name
        self.instruction_name = instruction_name


class _HdsConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO)

        self._tp = TextParser({
            'HDS': formatting.concept_(concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO),
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'symbol': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
            'symbols': formatting.concept(concepts.SYMBOL_CONCEPT_INFO.plural_name),
            'conf_params': formatting.concept(concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.plural_name),
            'PATH': syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
        })

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = []
        rest_paragraphs += self._tp.fnap(_MAIN_DESCRIPTION_REST)
        rest_paragraphs += self._directory_listing()

        sub_sections = [
            self._section(concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.singular_name.capitalize(),
                          _CONFIGURATION_PARAMETER),
            self._section('Relative paths',
                          _RELATIVITY),
            self._section(self._tp.format('Builtin {symbols} and environment variables'),
                          _BUILTIN_SYMBOL_ENVIRONMENT_VARIABLE),
        ]
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs, sub_sections))

    def _section(self, header: str, text_to_format: str) -> docs.Section:
        return docs.section(header,
                            self._tp.fnap(text_to_format))

    def see_also_targets(self) -> list:
        ret_val = [
            concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.cross_reference_target
        ]
        ret_val += [
            dir_info.conf_param.cross_reference_target
            for dir_info in _ALL_DIRECTORIES
        ]
        ret_val += [
            TestCasePhaseInstructionCrossReference(phase_identifier.CONFIGURATION.identifier,
                                                   dir_info.instruction_name)
            for dir_info in _ALL_DIRECTORIES
        ]
        return ret_val

    def _directory_listing(self) -> list:
        items = [
            self._dir_item(d)
            for d in _ALL_DIRECTORIES
        ]
        return [
            docs.simple_list(items, lists.ListType.VARIABLE_LIST)
        ]

    def _dir_item(self, x: _DirInfo) -> HeaderContentListItem:
        def prop_row(header: str, value_str_or_text) -> list:
            return [docs.text_cell(header),
                    docs.text_cell(value_str_or_text),
                    ]

        from exactly_lib.test_case_file_structure.relative_path_options import REL_HOME_OPTIONS_MAP
        properties_table = docs.first_column_is_header_table(
            [
                prop_row('Default value',
                         x.default_value_description),
                prop_row(concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.singular_name.capitalize(),
                         x.conf_param.configuration_parameter_name_text),
                prop_row('Set by instruction',
                         instruction_name_text(x.instruction_name)),
                prop_row('Variable name',
                         REL_HOME_OPTIONS_MAP[x.relativity_option_type].directory_variable_name_text),
                prop_row('Relativity option',
                         REL_HOME_OPTIONS_MAP[x.relativity_option_type].option_name_text),
            ]
        )

        paras = [
            docs.para(x.conf_param.single_line_description_str),
            properties_table,
        ]
        return docs.list_item(self._tp.text(x.item_name), paras)


HOME_DIRECTORY_STRUCTURE_CONCEPT = _HdsConcept()

_HOME_CASE_DIR_INFO = _DirInfo(
    RelHomeOptionType.REL_HOME_CASE,
    tc_fs.HDS_CASE_INFO,
    conf_params.HOME_CASE_DIRECTORY_CONF_PARAM_INFO,
    instruction_names.HOME_CASE_DIRECTORY_INSTRUCTION_NAME,
)

_HOME_ACT_DIR_INFO = _DirInfo(
    RelHomeOptionType.REL_HOME_ACT,
    tc_fs.HDS_ACT_INFO,
    conf_params.HOME_ACT_DIRECTORY_CONF_PARAM_INFO,
    instruction_names.HOME_ACT_DIRECTORY_INSTRUCTION_NAME,
)

_ALL_DIRECTORIES = (
    _HOME_ACT_DIR_INFO,
    _HOME_CASE_DIR_INFO,
)

_MAIN_DESCRIPTION_REST = """\
Typically, the directories in the {HDS} exist before the test case is executed.
They contain files read by, but not modified by, the test case.


Directories:
"""

_CONFIGURATION_PARAMETER = """
Each of these directories can be set in {phase[conf]:syntax},
since they are {conf_params}.

They cannot be set after {phase[conf]:syntax}.
"""

_RELATIVITY = """
{PATH} values have an option for referring to each of these directories.
"""

_BUILTIN_SYMBOL_ENVIRONMENT_VARIABLE = """
There is a builtin {symbol}, and an environment variable with the same name,
for each of these directories.
"""
