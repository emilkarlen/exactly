from exactly_lib.definitions.cross_ref.app_cross_ref import CrossReferenceId
from exactly_lib.util.textformat.construction.section_hierarchy.generator import SectionItemGeneratorEnvironment
from exactly_lib.util.textformat.construction.section_hierarchy.targets import CrossReferenceTextConstructor
from exactly_lib.util.textformat.structure.core import Text, StringText


class CrossReferenceTextConstructorTestImpl(CrossReferenceTextConstructor):
    def apply(self, x: CrossReferenceId) -> Text:
        return StringText('Reference to ' + str(x))


TEST_GENERATOR_ENVIRONMENT = SectionItemGeneratorEnvironment(set())
