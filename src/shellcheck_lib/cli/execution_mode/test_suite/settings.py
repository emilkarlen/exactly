import pathlib

from shellcheck_lib.test_case.sections.act.phase_setup import ActPhaseSetup


class Settings:
    def __init__(self,
                 act_phase_setup: ActPhaseSetup,
                 suite_root_file_path: pathlib.Path):
        self.__act_phase_setup = act_phase_setup
        self.__suite_root_file_path = suite_root_file_path

    @property
    def act_phase_setup(self) -> ActPhaseSetup:
        return self.__act_phase_setup

    @property
    def suite_root_file_path(self) -> pathlib.Path:
        return self.__suite_root_file_path
