from shellcheck_lib.help.program_modes.test_case.contents.phase.utils import pwd_at_start_of_phase_for_non_first_phases, \
    env_vars_up_to_act__TODO_CHECK_THIS
from shellcheck_lib.help.program_modes.test_case.phase_help_contents_structures import \
    TestCasePhaseHelpForPhaseWithoutInstructions, PhaseSequenceInfo, ExecutionEnvironmentInfo
from shellcheck_lib.help.utils.description import Description, single_line_description
from shellcheck_lib.util.textformat.structure.paragraph import para


class ActPhaseHelp(TestCasePhaseHelpForPhaseWithoutInstructions):
    def __init__(self,
                 name: str):
        super().__init__(name)

    def purpose(self) -> Description:
        return single_line_description('TODO the purpose of the %s phase' % self._name_as_header)

    def sequence_info(self) -> PhaseSequenceInfo:
        return PhaseSequenceInfo([para('TODO before ' + self._name_as_header)],
                                 [para('TODO after ' + self._name_as_header)])

    def is_mandatory(self) -> bool:
        return True

    def contents_description(self) -> list:
        return [para('TODO description of the contents of the %s phase.' % self._name_as_header)]

    def execution_environment_info(self) -> ExecutionEnvironmentInfo:
        return ExecutionEnvironmentInfo(pwd_at_start_of_phase_for_non_first_phases(),
                                        env_vars_up_to_act__TODO_CHECK_THIS())
