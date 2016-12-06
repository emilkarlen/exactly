from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.utils import append_section_if_contents_is_non_empty

SEE_ALSO_TITLE = docs.text('See also')
SEE_ALSO_TITLE__UPPERCASE = docs.text('SEE ALSO')


def cross_reference_list_paragraph(cross_references: list,
                                   environment: RenderingEnvironment) -> ParagraphItem:
    """
    :type cross_references: [CrossReferenceTarget]
    :return: A ParagraphItem that displays a list of cross references.
    """
    return docs.simple_header_only_list([environment.cross_ref_text_constructor.apply(cross_ref)
                                         for cross_ref in cross_references],
                                        lists.ListType.ITEMIZED_LIST)


def cross_reference_list_paragraphs(cross_references: list,
                                    environment: RenderingEnvironment) -> list:
    """
    :type cross_references: [CrossReferenceTarget]
    :return: [] if no cross references, else a list of a single `ParagraphItem`
    """
    if not cross_references:
        return []
    return [cross_reference_list_paragraph(cross_references, environment)]


def cross_reference_sections(cross_references: list,
                             rendering_environment: RenderingEnvironment,
                             uppercase_title: bool = False) -> list:
    """
    :return: An empty list of no cross-references, otherwise a singleton list.
    """
    ret_val = []
    title = SEE_ALSO_TITLE__UPPERCASE if uppercase_title else SEE_ALSO_TITLE
    append_section_if_contents_is_non_empty(
        ret_val,
        title,
        cross_reference_list_paragraphs(cross_references,
                                        rendering_environment))
    return ret_val
