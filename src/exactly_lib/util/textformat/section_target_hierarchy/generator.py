from exactly_lib.util.textformat.section_target_hierarchy.section_node import SectionItemNode
from exactly_lib.util.textformat.section_target_hierarchy.targets import TargetInfoFactory


class SectionHierarchyGenerator:
    """
    Generates a section with sub sections that may appear in a TOC.

    Can be put anywhere in a section hierarchy - it does not have
    a fixed position.
    """

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        """
        :param target_factory: Represents the root position of the generated
        section
        """
        raise NotImplementedError()
