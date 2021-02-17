from typing import Optional

from exactly_lib.execution.partial_execution.execution import MkSetupSettingsHandler
from exactly_lib.execution.partial_execution.setup_settings_handler import StandardSetupSettingsHandler
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.phases.setup.settings_handler import SetupSettingsHandler


def from_optional(x: Optional[SetupSettingsHandler]) -> SetupSettingsHandler:
    return (
        StandardSetupSettingsHandler.new_empty()
        if x is None
        else
        x
    )


def mk_from_optional(x: Optional[MkSetupSettingsHandler]) -> MkSetupSettingsHandler:
    return (
        StandardSetupSettingsHandler.new_from_environ
        if x is None
        else
        x
    )


def builder_from_optional(x: Optional[SetupSettingsBuilder]) -> SetupSettingsBuilder:
    return (
        SetupSettingsBuilder.new_empty()
        if x is None
        else
        x
    )
