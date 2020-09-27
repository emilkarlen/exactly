from typing import List

from exactly_lib import program_info
from exactly_lib.common.help import headers
from exactly_lib.definitions import test_case_file_structure as tc_fs, formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.doc_format import instruction_name_text
from exactly_lib.definitions.entity import concepts, conf_params, syntax_elements, types
from exactly_lib.definitions.entity.all_entity_types import BUILTIN_SYMBOL_ENTITY_TYPE_NAMES
from exactly_lib.definitions.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.definitions.test_case import phase_names, phase_infos
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.structure.lists import HeaderContentListItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class _DirInfo:
    def __init__(self,
                 relativity_option_type: RelHdsOptionType,
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
        super().__init__(concepts.HDS_CONCEPT_INFO)

        self._tp = TextParser({
            'HDS': concepts.HDS_CONCEPT_INFO.acronym,
            'hds_concept': formatting.concept_(concepts.HDS_CONCEPT_INFO),
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'symbol': formatting.concept_(concepts.SYMBOL_CONCEPT_INFO),
            'symbols': formatting.concept(concepts.SYMBOL_CONCEPT_INFO.plural_name),
            'conf_params': formatting.concept(concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.plural_name),
            'PATH': syntax_elements.PATH_SYNTAX_ELEMENT.singular_name,
            'Note': headers.NOTE_LINE_HEADER,
        })

    def purpose(self) -> DescriptionWithSubSections:
        sub_sections = [
            self._tp.section(concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.plural_name.capitalize(),
                             _CONFIGURATION_PARAMETER),
            self._tp.section('Relative paths',
                             _RELATIVITY),
            self._tp.section(self._tp.format(BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.name.plural.capitalize()),
                             _BUILTIN_SYMBOL),
            docs.section('Directories',
                         self._directory_listing()),
        ]
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(self._tp.fnap(_MAIN_DESCRIPTION_REST),
                                                          sub_sections))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        ret_val = [
            concepts.TCDS_CONCEPT_INFO.cross_reference_target,
            concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.cross_reference_target,
            concepts.SYMBOL_CONCEPT_INFO.cross_reference_target,
            types.PATH_TYPE_INFO.cross_reference_target,
        ]
        ret_val += [
            dir_info.conf_param.cross_reference_target
            for dir_info in _ALL_DIRECTORIES
        ]
        ret_val += [
            phase_infos.CONFIGURATION.instruction_cross_reference_target(dir_info.instruction_name)
            for dir_info in _ALL_DIRECTORIES
        ]
        return ret_val

    def _directory_listing(self) -> List[docs.ParagraphItem]:
        items = [
            self._dir_item(d)
            for d in _ALL_DIRECTORIES
        ]
        return [
            docs.simple_list(items, lists.ListType.VARIABLE_LIST)
        ]

    def _dir_item(self, x: _DirInfo) -> HeaderContentListItem:
        def prop_row(header: str, value_str_or_text) -> List[docs.TableCell]:
            return [docs.text_cell(header),
                    docs.text_cell(value_str_or_text),
                    ]

        from exactly_lib.tcfs.relative_path_options import REL_HDS_OPTIONS_MAP
        properties_table = docs.first_column_is_header_table(
            [
                prop_row('Default value',
                         x.default_value_description),
                prop_row(concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.singular_name.capitalize(),
                         x.conf_param.configuration_parameter_name_text),
                prop_row('Set by instruction',
                         instruction_name_text(x.instruction_name)),
                prop_row(BUILTIN_SYMBOL_ENTITY_TYPE_NAMES.name.singular.capitalize(),
                         REL_HDS_OPTIONS_MAP[x.relativity_option_type].directory_symbol_name_text),
                prop_row('Path relativity option',
                         REL_HDS_OPTIONS_MAP[x.relativity_option_type].option_name_text),
            ]
        )

        paras = [
            docs.para(x.conf_param.single_line_description_str),
            properties_table,
        ]
        return docs.list_item(self._tp.text(x.item_name), paras)


HDS_CONCEPT = _HdsConcept()

_HDS_CASE_DIR_INFO = _DirInfo(
    RelHdsOptionType.REL_HDS_CASE,
    tc_fs.HDS_CASE_INFO,
    conf_params.HDS_CASE_DIRECTORY_CONF_PARAM_INFO,
    instruction_names.HDS_CASE_DIRECTORY_INSTRUCTION_NAME,
)

_HDS_ACT_DIR_INFO = _DirInfo(
    RelHdsOptionType.REL_HDS_ACT,
    tc_fs.HDS_ACT_INFO,
    conf_params.HDS_ACT_DIRECTORY_CONF_PARAM_INFO,
    instruction_names.HDS_ACT_DIRECTORY_INSTRUCTION_NAME,
)

_ALL_DIRECTORIES = (
    _HDS_ACT_DIR_INFO,
    _HDS_CASE_DIR_INFO,
)

_MAIN_DESCRIPTION_REST = """\
The directories in the {hds_concept} ({HDS}) exist before the test case is executed.
They contain files read by, but not modified by, the test case.


{program_name} prevents modification of the contents of these directories,
by preventing them from being used by modification operations.


{Note} {program_name} cannot prevent an external program from
modifying their contents.
"""

_CONFIGURATION_PARAMETER = """
Each of these directories can be set in {phase[conf]:syntax},
since they are {conf_params}.

They cannot be set after {phase[conf]:syntax}.
"""

_RELATIVITY = """
{PATH} values have an option for referring to each of these directories.
"""

_BUILTIN_SYMBOL = """
There is a builtin {PATH} {symbol}
for each of these directories.
"""
