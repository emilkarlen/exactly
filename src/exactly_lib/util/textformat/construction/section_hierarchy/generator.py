from exactly_lib.util.textformat.construction.section_hierarchy.section_node import SectionItemNode
from exactly_lib.util.textformat.construction.section_hierarchy.targets import TargetInfoFactory


class SectionHierarchyGenerator:
    """
    Generates a section with sub sections that that appear in the TOC.

    Can be put anywhere in the section hierarchy,
    since it takes an `TargetInfoFactory` as input and uses that to
    generate nodes.
    """

    def generate(self, target_factory: TargetInfoFactory) -> SectionItemNode:
        raise NotImplementedError()
