import pathlib

from exactly_lib.test_case.phases.configuration import ConfigurationBuilder
from exactly_lib_test.test_case.actor.test_resources.actors import \
    actor_that_must_not_be_used


def arbitrary_configuration_builder() -> ConfigurationBuilder:
    cwd = pathlib.Path.cwd()
    return ConfigurationBuilder(home_case_dir_path=cwd,
                                home_act_dir_path=cwd,
                                actor=actor_that_must_not_be_used(),
                                timeout_in_seconds=None)
