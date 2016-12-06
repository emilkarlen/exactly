from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem


def cross_reference_list(cross_references: list,
                         environment: RenderingEnvironment) -> ParagraphItem:
    """
    :type cross_references: [CrossReferenceTarget]
    :return: A ParagraphItem that displays a list of cross references.
    """
    return docs.simple_header_only_list([environment.cross_ref_text_constructor.apply(cross_ref)
                                         for cross_ref in cross_references],
                                        lists.ListType.ITEMIZED_LIST)
