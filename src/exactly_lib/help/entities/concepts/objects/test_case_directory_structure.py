from typing import List

from exactly_lib import program_info
from exactly_lib.definitions import formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import SingularAndPluralNameAndCrossReferenceId
from exactly_lib.definitions.entity import concepts, syntax_elements, types
from exactly_lib.definitions.test_case_file_structure import HDS_DIR_INFOS_IN_DISPLAY_ORDER, \
    SDS_DIR_INFOS_IN_DISPLAY_ORDER, TcDirInfo
from exactly_lib.help.entities.concepts.contents_structure import ConceptDocumentation
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.document import SectionContents
from exactly_lib.util.textformat.textformat_parser import TextParser


class _TcdsConcept(ConceptDocumentation):
    def __init__(self):
        super().__init__(concepts.TCDS_CONCEPT_INFO)

        self._tp = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'path_type': formatting.entity_(types.PATH_TYPE_INFO)
        })

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = []
        sub_sections = []
        rest_paragraphs += self._tp.fnap(_MAIN_DESCRIPTION_REST)
        rest_paragraphs += self._dir_structure_list()
        rest_paragraphs += self._tp.fnap(_MAIN_DESCRIPTION_LAST)
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs, sub_sections))

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            concepts.HDS_CONCEPT_INFO.cross_reference_target,
            concepts.SDS_CONCEPT_INFO.cross_reference_target,
            syntax_elements.PATH_SYNTAX_ELEMENT.cross_reference_target,
        ]

    def _dir_structure_list(self) -> List[docs.ParagraphItem]:
        items = [
            self._dir_structure_item(concept, tc_dir_infos)
            for concept, tc_dir_infos in _DIR_STRUCTURES
        ]
        return [
            docs.simple_list_with_space_between_elements_and_content(items, lists.ListType.ITEMIZED_LIST)
        ]

    def _dir_structure_item(self,
                            dir_structure: SingularAndPluralNameAndCrossReferenceId,
                            tc_dir_infos: List[TcDirInfo],
                            ) -> lists.HeaderContentListItem:
        contents = [
            docs.para(dir_structure.single_line_description),
            self._dirs_list(tc_dir_infos)
        ]
        return docs.list_item(dir_structure.singular_name.capitalize(),
                              contents)

    def _dirs_list(self, tc_dir_infos: List[TcDirInfo]) -> docs.ParagraphItem:
        return docs.first_column_is_header_table([
            self._dir_row(tc_dir_info)
            for tc_dir_info in tc_dir_infos
        ])

    def _dir_row(self, tc_dir_info: TcDirInfo) -> List[docs.TableCell]:
        return [
            docs.text_cell(tc_dir_info.informative_name),
            docs.text_cell(tc_dir_info.single_line_description_str),
        ]


TEST_CASE_DIRECTORY_STRUCTURE_CONCEPT = _TcdsConcept()

_DIR_STRUCTURES = (
    (
        concepts.HDS_CONCEPT_INFO,
        HDS_DIR_INFOS_IN_DISPLAY_ORDER,
    ),
    (
        concepts.SDS_CONCEPT_INFO,
        SDS_DIR_INFOS_IN_DISPLAY_ORDER,
    ),
)

_MAIN_DESCRIPTION_REST = """\
Consists of two sets of directories:
"""

_MAIN_DESCRIPTION_LAST = """\
{program_name} has support for referring to all of these directories
from a test case via the {path_type} type.
"""
