from shellcheck_lib.help import cross_reference_id as cross_ref
from shellcheck_lib.help.program_modes.test_case.contents.main.intro_environment import execution_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.intro_phases import phases_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.intro_test_case import test_case_intro_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.ref_test_case_files import test_case_files_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.ref_test_case_processing import \
    test_case_processing_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.test_outcome import test_outcome_documentation
from shellcheck_lib.help.program_modes.test_case.contents.main.utils import Setup, TestCaseHelpRendererBase
from shellcheck_lib.help.program_modes.test_case.contents_structure import TestCaseHelp
from shellcheck_lib.help.utils.render import RenderingEnvironment
from shellcheck_lib.util.textformat.structure import core
from shellcheck_lib.util.textformat.structure import document as doc
from shellcheck_lib.util.textformat.structure.structures import para

ONE_LINE_DESCRIPTION = "Executes a program in a temporary sandbox directory and checks it's result."


class OverviewTargets:
    def __init__(self,
                 overview_target: core.CrossReferenceTarget = None,
                 outcome_target: core.CrossReferenceTarget = None):
        self.overview_target = overview_target
        self.outcome_target = outcome_target


class OverviewRenderer(TestCaseHelpRendererBase):
    def __init__(self, test_case_help: TestCaseHelp,
                 target_factory: cross_ref.CustomTargetInfoFactory = None):
        super().__init__(test_case_help)
        if target_factory is None:
            target_factory = cross_ref.CustomTargetInfoFactory('')

        ow_taget_factory = cross_ref.sub_component_factory('overview',
                                                           target_factory)

        self._OVERVIEW_TI = target_factory.make('Overview',
                                                'overview')

        self._OV__TEST_CASES_TI = ow_taget_factory.make('Test cases',
                                                        'test-cases')

        self._OV__ENVIRONMENT_TI = ow_taget_factory.make('Environment',
                                                         'environment')

        self._OV__PHASES_TI = ow_taget_factory.make('Phases',
                                                    'phases')

        self._OUTCOME_TI = target_factory.make('Test Outcome',
                                               'outcome')

        self._TEST_CASE_FILES_TI = target_factory.make('Test Case Files',
                                                       'test-case-files')

        self._TEST_CASE_PROCESSING_TI = target_factory.make('Test Case Processing',
                                                            'test-case-processing')

    def target_info_hierarchy(self) -> list:
        return [
            cross_ref.TargetInfoNode(self._OVERVIEW_TI, [
                _leaf(self._OV__TEST_CASES_TI),
                _leaf(self._OV__ENVIRONMENT_TI),
                _leaf(self._OV__PHASES_TI),

            ]),
            _leaf(self._OUTCOME_TI),
            _leaf(self._TEST_CASE_FILES_TI),
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
                                    doc.Section(self._OV__TEST_CASES_TI.anchor_text(),
                                                test_case_intro_contents),
                                    doc.Section(self._OV__ENVIRONMENT_TI.anchor_text(),
                                                execution_contents),
                                    doc.Section(self._OV__PHASES_TI.anchor_text(),
                                                phases_contents),
                                ])),
                doc.Section(self._TEST_CASE_FILES_TI.anchor_text(),
                            test_case_files_documentation(setup)),
                doc.Section(self._TEST_CASE_PROCESSING_TI.anchor_text(),
                            test_case_processing_documentation(setup)),
                doc.Section(self._OUTCOME_TI.anchor_text(),
                            test_outcome_documentation(setup)),
            ])


_leaf = cross_ref.target_info_leaf
