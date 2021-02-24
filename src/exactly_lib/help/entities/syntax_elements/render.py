import functools
from typing import List, Iterable

from exactly_lib.common.help import headers
from exactly_lib.definitions.entity.all_entity_types import SYNTAX_ELEMENT_ENTITY_TYPE_NAMES
from exactly_lib.definitions.type_system import TypeCategory
from exactly_lib.help.contents_structure.entity import CliListConstructorGetter, HtmlDocHierarchyGeneratorGetter
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help.entities.types.render import LOGIC_TYPES_HEADER, DATA_TYPES_HEADER
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_paragraphs
from exactly_lib.help.render import partitioned_entity_set as pes
from exactly_lib.help.render.entity_docs import \
    single_line_description_as_summary_paragraphs
from exactly_lib.help.render.see_also import see_also_sections
from exactly_lib.util.textformat import utils as text_utils
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.utils import append_section_if_contents_is_non_empty


def _docs_of_type_category(category: TypeCategory,
                           element_doc_list: Iterable[SyntaxElementDocumentation]
                           ) -> List[SyntaxElementDocumentation]:
    return list(filter(lambda element_doc: element_doc.type_category is category,
                       element_doc_list))


_PARTITIONS_SETUP = [
    pes.PartitionSetup(pes.PartitionNamesSetup('data-type',
                                               DATA_TYPES_HEADER),
                       functools.partial(_docs_of_type_category, TypeCategory.DATA)
                       ),
    pes.PartitionSetup(pes.PartitionNamesSetup('logic-type',
                                               LOGIC_TYPES_HEADER),
                       functools.partial(_docs_of_type_category, TypeCategory.LOGIC)
                       ),
    pes.PartitionSetup(pes.PartitionNamesSetup('other',
                                               'Other'),
                       functools.partial(_docs_of_type_category, None)
                       ),
]


class IndividualSyntaxElementConstructor(ArticleContentsConstructor):
    def __init__(self, syntax_element: SyntaxElementDocumentation):
        self.syntax_element = syntax_element

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        initial_paragraphs = []
        invokation_variants = self.syntax_element.invokation_variants()
        if len(invokation_variants) > 1:
            initial_paragraphs.append(headers.FORMS_PARA)
        initial_paragraphs += invokation_variants_paragraphs(None,
                                                             invokation_variants,
                                                             self.syntax_element.syntax_element_descriptions())
        return doc.ArticleContents(docs.paras(self.syntax_element.single_line_description()),
                                   doc.SectionContents(initial_paragraphs,
                                                       self._sub_sections(environment)))

    def _sub_sections(self, environment: ConstructionEnvironment) -> List[doc.SectionItem]:
        ret_val = []
        append_section_if_contents_is_non_empty(ret_val,
                                                headers.DESCRIPTION__HEADER__CAPITALIZED,
                                                self.syntax_element.main_description_rest())
        ret_val += text_utils.maybe_section(headers.NOTES__HEADER__CAPITALIZED,
                                            self.syntax_element.notes())
        ret_val += see_also_sections(self.syntax_element.see_also_targets(), environment,
                                     uppercase_title=False)
        return ret_val


def hierarchy_generator_getter() -> HtmlDocHierarchyGeneratorGetter:
    return pes.PartitionedHierarchyGeneratorGetter(SYNTAX_ELEMENT_ENTITY_TYPE_NAMES.identifier,
                                                   _PARTITIONS_SETUP,
                                                   IndividualSyntaxElementConstructor)


def list_render_getter() -> CliListConstructorGetter:
    return pes.PartitionedCliListConstructorGetter(
        _PARTITIONS_SETUP,
        single_line_description_as_summary_paragraphs)
