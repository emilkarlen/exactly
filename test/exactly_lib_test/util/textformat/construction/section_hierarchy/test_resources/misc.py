from exactly_lib.help_texts.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.util.textformat.construction.section_hierarchy.structures import HierarchyGeneratorEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy.targets import CrossReferenceTextConstructor
from exactly_lib.util.textformat.structure.core import Text, StringText


class CrossReferenceTextConstructorTestImpl(CrossReferenceTextConstructor):
    def apply(self, x: CrossReferenceId) -> Text:
        return StringText('Reference to ' + str(x))


TEST_HIERARCHY_ENVIRONMENT = HierarchyGeneratorEnvironment(set())
