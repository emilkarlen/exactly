from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.help.program_modes.test_case.contents.main.utils import TestCaseHelpRendererBase, Setup
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.section_hierarchy_rendering import parent, leaf
from exactly_lib.util.textformat.structure import structures as docs
from . import intro, environment as env_doc, phases, test_case


class OverviewDocumentationRenderer(TestCaseHelpRendererBase):
    def __init__(self,
                 header: str,
                 setup: Setup,
                 target_factory: cross_ref.CustomTargetInfoFactory):
        super().__init__(setup.test_case_help)
        self.setup = setup
        self.target_factory = target_factory

        self.hierarchy = parent(header, [],
                                [
                                    ('introduction', leaf('Introduction', intro.Documentation(setup))),
                                    ('test-cases', leaf('Test cases', test_case.Documentation(setup))),
                                    ('environment', leaf('Environment', env_doc.Documentation(setup))),
                                    ('phases', leaf('Phases', phases.Documentation(setup))),
                                ]
                                )
        self.node = self.hierarchy.section_renderer_node(target_factory)
        self._INTRO_TI = target_factory.sub('Introduction', 'introduction')
        self._TEST_CASES_TI = target_factory.sub('Test cases', 'test-cases')
        self._ENVIRONMENT_TI = target_factory.sub('Environment', 'environment')
        self._PHASES_TI = target_factory.sub('Phases', 'phases')

    def target_info_hierarchy(self) -> list:
        return self.node.target_info_node()
        # return [
        #     cross_ref.target_info_leaf(self._INTRO_TI),
        #     cross_ref.target_info_leaf(self._TEST_CASES_TI),
        #     cross_ref.target_info_leaf(self._ENVIRONMENT_TI),
        #     cross_ref.target_info_leaf(self._PHASES_TI),
        # ]

    def apply(self, environment: RenderingEnvironment) -> docs.SectionContents:
        return self.hierarchy.section_renderer_node(self.target_factory).section_renderer().apply(environment)
        # return docs.SectionContents(
        #     [],
        #     [
        #         docs.Section(self._INTRO_TI.anchor_text(), intro.intro_intro_documentation(self.setup)),
        #         docs.Section(self._TEST_CASES_TI.anchor_text(), test_case.test_case_intro_documentation(self.setup)),
        #         docs.Section(self._ENVIRONMENT_TI.anchor_text(), env_doc.execution_documentation(self.setup)),
        #         docs.Section(self._PHASES_TI.anchor_text(), phases.phases_documentation(self.setup)),
        #     ])
