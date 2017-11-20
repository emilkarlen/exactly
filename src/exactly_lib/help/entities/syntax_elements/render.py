import functools

from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help.entities.types.render import LOGIC_TYPES_HEADER, DATA_TYPES_HEADER
from exactly_lib.help.program_modes.common.render_syntax_contents import invokation_variants_paragraphs
from exactly_lib.help.utils.rendering import parttioned_entity_set as pes
from exactly_lib.help.utils.rendering.entity_documentation_rendering import \
    single_line_description_as_summary_paragraphs
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.help.utils.rendering.see_also_section import see_also_sections
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.utils import append_section_if_contents_is_non_empty


def _docs_of_type_category(category: TypeCategory, element_doc_list: list) -> list:
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


class IndividualSyntaxElementRenderer(SectionContentsRenderer):
    def __init__(self, syntax_element: SyntaxElementDocumentation):
        self.syntax_element = syntax_element

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        initial_paragraphs = [docs.para(self.syntax_element.single_line_description())]
        invokation_variants = self.syntax_element.invokation_variants()
        if len(invokation_variants) > 1:
            initial_paragraphs.append(docs.para('Forms:'))
        initial_paragraphs += invokation_variants_paragraphs(None,
                                                             invokation_variants,
                                                             self.syntax_element.syntax_element_descriptions())
        return doc.SectionContents(initial_paragraphs,
                                   self._sub_sections(environment))

    def _sub_sections(self, environment: RenderingEnvironment) -> list:
        ret_val = []
        append_section_if_contents_is_non_empty(ret_val,
                                                'Description',
                                                self.syntax_element.main_description_rest())
        ret_val += see_also_sections(self.syntax_element.see_also_targets(), environment,
                                     uppercase_title=False)
        return ret_val


def hierarchy_generator_getter() -> pes.HtmlDocHierarchyGeneratorGetter:
    return pes.PartitionedHierarchyGeneratorGetter(_PARTITIONS_SETUP,
                                                   IndividualSyntaxElementRenderer)


def list_render_getter() -> pes.CliListRendererGetter:
    return pes.PartitionedCliListRendererGetter(
        _PARTITIONS_SETUP,
        single_line_description_as_summary_paragraphs)
