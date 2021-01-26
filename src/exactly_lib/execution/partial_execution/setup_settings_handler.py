from typing import Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation, resolve_optional
from exactly_lib.test_case.phases.act.execution_input import ActExecutionInput
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.phases.setup.settings_handler import SetupSettingsHandler
from exactly_lib.type_val_prims.string_source.string_source import StringSource


class StandardSetupSettingsHandler(SetupSettingsHandler):
    def __init__(self, builder: SetupSettingsBuilder):
        self._builder = builder

    @staticmethod
    def new_empty() -> SetupSettingsHandler:
        return StandardSetupSettingsHandler(SetupSettingsBuilder.new_empty())

    @property
    def builder(self) -> SetupSettingsBuilder:
        return self._builder

    def as_act_execution_input(self) -> AdvWValidation[ActExecutionInput]:
        return ActExecutionInputAdv(self._builder.stdin)


class ActExecutionInputAdv(AdvWValidation[ActExecutionInput]):
    """Configuration of stdin for the act phase, supplied to the ATC by the Actor."""

    def __init__(self, stdin: Optional[AdvWValidation[StringSource]]):
        self._stdin = stdin

    @staticmethod
    def empty() -> 'ActExecutionInputAdv':
        return ActExecutionInputAdv(None)

    def validate(self) -> Optional[TextRenderer]:
        return (
            None
            if self._stdin is None
            else
            self._stdin.validate()
        )

    def resolve(self, environment: ApplicationEnvironment) -> ActExecutionInput:
        return ActExecutionInput(
            resolve_optional(self._stdin, environment)
        )
