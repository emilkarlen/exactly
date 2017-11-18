from exactly_lib import program_info
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.help_texts.entity import concepts
from exactly_lib.help_texts.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case import phase_names
from exactly_lib.help_texts.test_case_file_structure import TcDirInfo
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class _HdsConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO)

        self._tp = TextParser({
            'HDS': formatting.concept_(concepts.HOME_DIRECTORY_STRUCTURE_CONCEPT_INFO),
            'phase': phase_names.PHASE_NAME_DICTIONARY,
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'conf_params': formatting.concept(concepts.CONFIGURATION_PARAMETER_CONCEPT_INFO.plural_name),
        })

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = []
        sub_sections = []
        rest_paragraphs += self._tp.fnap(_MAIN_DESCRIPTION_REST)
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs, sub_sections))

    def see_also_targets(self) -> list:
        return [
        ]


HOME_DIRECTORY_STRUCTURE_CONCEPT = _HdsConcept()

_MAIN_DESCRIPTION_REST = """\
Typically, the directories in the {HDS} exist before the test case is executed.
They contain files read by, but not modified by, the test case.


All of these directories are {conf_params}, which means that they can be set in {phase[conf]:syntax}.

The values cannot be changed after {phase[conf]:syntax}.


Directories:
"""


class DirInfo:
    def __init__(self,
                 dir_info: TcDirInfo,
                 conf_param: ConfigurationParameterInfo,
                 default_value_description: str,
                 relativity_option_type: RelHomeOptionType,
                 ):
        self.conf_param = conf_param
        self.relativity_option_type = relativity_option_type
        self.default_value_description = default_value_description
        self.conf_param = conf_param
        self.dir_info = dir_info
