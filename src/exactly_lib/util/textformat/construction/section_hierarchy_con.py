from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor
from exactly_lib.util.textformat.construction.section_hierarchy_constructor import SectionHierarchyGenerator, \
    _SectionLeafGenerator, _SectionHierarchyGeneratorWithSubSections
from exactly_lib.util.textformat.structure.core import StringText


def leaf(header: str,
         contents_renderer: SectionContentsConstructor) -> SectionHierarchyGenerator:
    """A section without sub sections that appear in the TOC/target hierarchy"""
    return _SectionLeafGenerator(StringText(header), contents_renderer)


def parent(header: str,
           initial_paragraphs: list,
           local_target_name__sub_section__list: list,
           ) -> SectionHierarchyGenerator:
    """
    A section with sub sections that appear in the TOC/target hierarchy.
    :param local_target_name__sub_section__list: [(str, SectionHierarchyGenerator)]
    :param initial_paragraphs: [ParagraphItem]
    """
    return _SectionHierarchyGeneratorWithSubSections(StringText(header),
                                                     initial_paragraphs,
                                                     local_target_name__sub_section__list)
