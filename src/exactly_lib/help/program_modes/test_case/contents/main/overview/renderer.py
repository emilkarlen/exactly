from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.help.program_modes.test_case.contents.main.utils import TestCaseHelpRendererBase, Setup
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.textformat.structure import structures as docs
from . import intro, environment as env_doc, phases, test_case


class OverviewDocumentationRenderer(TestCaseHelpRendererBase):
    def __init__(self, setup: Setup,
                 target_factory: cross_ref.CustomTargetInfoFactory):
        super().__init__(setup.test_case_help)
        self.setup = setup

        self._INTRO_TI = target_factory.sub('Introduction', 'introduction')
        self._TEST_CASES_TI = target_factory.sub('Test cases', 'test-cases')
        self._ENVIRONMENT_TI = target_factory.sub('Environment', 'environment')
        self._PHASES_TI = target_factory.sub('Phases', 'phases')

    def target_info_hierarchy(self) -> list:
        return [
            cross_ref.target_info_leaf(self._INTRO_TI),
            cross_ref.target_info_leaf(self._TEST_CASES_TI),
            cross_ref.target_info_leaf(self._ENVIRONMENT_TI),
            cross_ref.target_info_leaf(self._PHASES_TI),
        ]

    def apply(self, environment: RenderingEnvironment) -> docs.SectionContents:
        return docs.SectionContents(
            [],
            [
                docs.Section(self._INTRO_TI.anchor_text(), intro.intro_intro_documentation(self.setup)),
                docs.Section(self._TEST_CASES_TI.anchor_text(), test_case.test_case_intro_documentation(self.setup)),
                docs.Section(self._ENVIRONMENT_TI.anchor_text(), env_doc.execution_documentation(self.setup)),
                docs.Section(self._PHASES_TI.anchor_text(), phases.phases_documentation(self.setup)),
            ])
