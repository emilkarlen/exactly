from typing import Optional, Mapping

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation, resolve_optional
from exactly_lib.test_case.phases.act.execution_input import AtcExecutionInput
from exactly_lib.test_case.phases.environ import OptionalEnvVarsDict
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.phases.setup.settings_handler import SetupSettingsHandler
from exactly_lib.type_val_prims.string_source.string_source import StringSource


class StandardSetupSettingsHandler(SetupSettingsHandler):
    def __init__(self, builder: SetupSettingsBuilder):
        self._builder = builder

    @staticmethod
    def new_empty() -> SetupSettingsHandler:
        return StandardSetupSettingsHandler(SetupSettingsBuilder.new_empty())

    @staticmethod
    def new_from_environ(environ: OptionalEnvVarsDict) -> SetupSettingsHandler:
        return StandardSetupSettingsHandler(SetupSettingsBuilder(None, environ))

    @property
    def builder(self) -> SetupSettingsBuilder:
        return self._builder

    def as_atc_execution_input(self) -> AdvWValidation[AtcExecutionInput]:
        return AtcExecutionInputAdv(self._builder.stdin, self._builder.environ)


class AtcExecutionInputAdv(AdvWValidation[AtcExecutionInput]):
    """Configuration of stdin for the act phase, supplied to the ATC by the Actor."""

    def __init__(self,
                 stdin: Optional[AdvWValidation[StringSource]],
                 environ: Optional[Mapping[str, str]],
                 ):
        self._stdin = stdin
        self._environ = environ

    @staticmethod
    def empty() -> 'AtcExecutionInputAdv':
        return AtcExecutionInputAdv(None, None)

    @property
    def environ(self) -> Optional[Mapping[str, str]]:
        """
        :return: (immutable) None if inherit current process' environment
        """
        return self._environ

    def validate(self) -> Optional[TextRenderer]:
        return (
            None
            if self._stdin is None
            else
            self._stdin.validate()
        )

    def resolve(self, environment: ApplicationEnvironment) -> AtcExecutionInput:
        return AtcExecutionInput(
            resolve_optional(self._stdin, environment),
            self._environ,
        )
