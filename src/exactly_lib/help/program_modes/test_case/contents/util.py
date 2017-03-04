from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.help.utils import section_hierarchy_rendering as hierarchy_rendering
from exactly_lib.help.utils.section_contents_renderer import SectionContentsRenderer, RenderingEnvironment
from exactly_lib.section_document.model import SectionContents


class SectionContentsRendererWithSetup(SectionContentsRenderer):
    def __init__(self, setup: Setup):
        self.setup = setup


class SectionFromGeneratorAsSectionContentsRenderer(SectionContentsRenderer):
    """
    Transforms a `SectionGenerator` to a `SectionContentsRenderer`,
    for usages where section header and target hierarchy is irrelevant.
    """

    def __init__(self, generator: hierarchy_rendering.SectionGenerator):
        self.generator = generator

    def apply(self, environment: RenderingEnvironment) -> SectionContents:
        target_factory = hierarchy_rendering.CustomTargetInfoFactory('arbitrary')
        return self.generator.section_renderer_node(target_factory).section(environment).contents
