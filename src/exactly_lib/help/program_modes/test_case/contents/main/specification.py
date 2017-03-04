from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.common.help.cross_reference_id import sub_component_factory
from exactly_lib.help.program_modes.test_case.contents.main import ref_test_case_files as tc
from exactly_lib.help.program_modes.test_case.contents.main import ref_test_case_processing as processing
from exactly_lib.help.program_modes.test_case.contents.main import test_outcome
from exactly_lib.help.program_modes.test_case.contents.main.overview import renderer as overview
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup, TestCaseHelpRendererBase
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.utils import section_hierarchy_rendering as hierarchy_rendering
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import para

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


def generator(header: str, test_case_help: TestCaseHelp) -> hierarchy_rendering.SectionGenerator:
    setup = Setup(test_case_help)
    return hierarchy_rendering.parent(
        header,
        [],
        [
            ('overview', overview.generator('Overview', setup)),
            ('outcome', hierarchy_rendering.leaf('Test outcome', test_outcome.TestOutcomeDocumentation(setup))),
            ('file-syntax', tc.generator('Test case file syntax', setup)),
            ('processing', hierarchy_rendering.leaf('Test case processing', processing.ContentsRenderer(setup))),
        ])


class SpecificationRenderer(TestCaseHelpRendererBase):
    def __init__(self, test_case_help: TestCaseHelp,
                 target_factory: cross_ref.CustomTargetInfoFactory = None):
        super().__init__(test_case_help)
        self.setup = Setup(self.test_case_help)
        if target_factory is None:
            target_factory = cross_ref.CustomTargetInfoFactory('')

        overview_generator = overview.generator('Overview', self.setup)
        self._overview_section_renderer_node = overview_generator.section_renderer_node(
            target_factory.sub_factory('overview'))
        outcome_generator = hierarchy_rendering.leaf('Test outcome', test_outcome.TestOutcomeDocumentation(self.setup))
        self._outcome_node = outcome_generator.section_renderer_node(sub_component_factory('outcome', target_factory))

        _file_target_factory = cross_ref.sub_component_factory('file-syntax',
                                                               target_factory)
        test_case_generator = tc.generator('Test case file syntax', self.setup)
        self._tc_section_renderer_node = test_case_generator.section_renderer_node(
            _file_target_factory)

        processing_generator = hierarchy_rendering.leaf('Test case processing', processing.ContentsRenderer(self.setup))
        self._processing_node = processing_generator.section_renderer_node(
            target_factory.sub_factory('test-case-processing'))

    def target_info_hierarchy(self) -> list:
        return [
            self._overview_section_renderer_node.target_info_node(),
            self._outcome_node.target_info_node(),
            self._tc_section_renderer_node.target_info_node(),
            self._processing_node.target_info_node(),
        ]

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents(
            [para(ONE_LINE_DESCRIPTION)],
            [
                self._overview_section_renderer_node.section(environment),
                self._tc_section_renderer_node.section(environment),
                self._processing_node.section(environment),
                self._outcome_node.section(environment),
            ])


_leaf = cross_ref.target_info_leaf
