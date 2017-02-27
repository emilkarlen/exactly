from exactly_lib.common.help import cross_reference_id as cross_ref
from exactly_lib.help.program_modes.test_case.contents.main.intro_environment import execution_documentation
from exactly_lib.help.program_modes.test_case.contents.main.intro_intro import intro_intro_documentation
from exactly_lib.help.program_modes.test_case.contents.main.intro_phases import phases_documentation
from exactly_lib.help.program_modes.test_case.contents.main.intro_test_case import test_case_intro_documentation
from exactly_lib.help.program_modes.test_case.contents.main.ref_test_case_files import TestCaseFileDocumentationRenderer
from exactly_lib.help.program_modes.test_case.contents.main.ref_test_case_processing import \
    test_case_processing_documentation
from exactly_lib.help.program_modes.test_case.contents.main.test_outcome import test_outcome_documentation
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup, TestCaseHelpRendererBase
from exactly_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import para

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


class SpecificationRenderer(TestCaseHelpRendererBase):
    def __init__(self, test_case_help: TestCaseHelp,
                 target_factory: cross_ref.CustomTargetInfoFactory = None):
        super().__init__(test_case_help)
        self.setup = Setup(self.test_case_help)
        if target_factory is None:
            target_factory = cross_ref.CustomTargetInfoFactory('')

        ow_target_factory = cross_ref.sub_component_factory('overview',
                                                            target_factory)

        self._OVERVIEW_TI = ow_target_factory.root('Overview')

        self._OV__INTRO_TI = ow_target_factory.sub('Introduction',
                                                   'introduction')

        self._OV__TEST_CASES_TI = ow_target_factory.sub('Test cases',
                                                        'test-cases')

        self._OV__ENVIRONMENT_TI = ow_target_factory.sub('Environment',
                                                         'environment')

        self._OV__PHASES_TI = ow_target_factory.sub('Phases',
                                                    'phases')

        self._OUTCOME_TI = target_factory.sub('Test outcome',
                                              'outcome')

        self._file_target_factory = cross_ref.sub_component_factory('file-syntax',
                                                                    target_factory)
        self._TEST_CASE_FILES_TI = self._file_target_factory.root('Test case file syntax')
        self._test_case_file_renderer = TestCaseFileDocumentationRenderer(self.setup,
                                                                          self._file_target_factory)

        self._TEST_CASE_PROCESSING_TI = target_factory.sub('Test case processing',
                                                           'test-case-processing')

    def target_info_hierarchy(self) -> list:
        return [
            cross_ref.TargetInfoNode(self._OVERVIEW_TI, [
                _leaf(self._OV__INTRO_TI),
                _leaf(self._OV__TEST_CASES_TI),
                _leaf(self._OV__ENVIRONMENT_TI),
                _leaf(self._OV__PHASES_TI),

            ]),
            _leaf(self._OUTCOME_TI),
            cross_ref.TargetInfoNode(self._TEST_CASE_FILES_TI,
                                     self._test_case_file_renderer.target_info_hierarchy()),
            _leaf(self._TEST_CASE_PROCESSING_TI),
        ]

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        setup = Setup(self.test_case_help)
        test_case_intro_contents = test_case_intro_documentation(setup)
        phases_contents = phases_documentation(setup)
        execution_contents = execution_documentation(setup)
        return doc.SectionContents(
            [para(ONE_LINE_DESCRIPTION)],
            [
                doc.Section(self._OVERVIEW_TI.anchor_text(),
                            doc.SectionContents(
                                [],
                                [
                                    doc.Section(self._OV__INTRO_TI.anchor_text(),
                                                intro_intro_documentation(setup)),
                                    doc.Section(self._OV__TEST_CASES_TI.anchor_text(),
                                                test_case_intro_contents),
                                    doc.Section(self._OV__ENVIRONMENT_TI.anchor_text(),
                                                execution_contents),
                                    doc.Section(self._OV__PHASES_TI.anchor_text(),
                                                phases_contents),
                                ])),
                doc.Section(self._TEST_CASE_FILES_TI.anchor_text(),
                            self._test_case_file_renderer.apply(environment)),
                doc.Section(self._TEST_CASE_PROCESSING_TI.anchor_text(),
                            test_case_processing_documentation(setup)),
                doc.Section(self._OUTCOME_TI.anchor_text(),
                            test_outcome_documentation(setup)),
            ])


_leaf = cross_ref.target_info_leaf
