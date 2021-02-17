from typing import Dict, List, Callable, Sequence

from exactly_lib.impls.instructions.multi_phase.environ.impl import Phase
from exactly_lib.util.name_and_value import NameAndValue

EnvVar = NameAndValue[str]
EnvVarDict = Dict[str, str]


class EnvironsSetup:
    def __init__(self,
                 the_act: List[EnvVar],
                 non_act: List[EnvVar],
                 ):
        self.the_act = the_act
        self.non_act = non_act

    @staticmethod
    def of_non_act(non_act: List[EnvVar]) -> 'EnvironsSetup':
        return EnvironsSetup(the_act=[], non_act=non_act)

    def new_with_added(self,
                       the_act: EnvVar,
                       non_act: EnvVar,
                       ) -> 'EnvironsSetup':
        return EnvironsSetup(
            self.the_act + [the_act],
            self.non_act + [non_act],
        )

    def new_with_removed(self, var_name_to_remove: str, ) -> 'EnvironsSetup':
        return EnvironsSetup(
            the_act=[var for var in self.the_act
                     if var.name != var_name_to_remove],
            non_act=[var for var in self.non_act
                     if var.name != var_name_to_remove],
        )

    def env_vars(self, phase: Phase) -> List[EnvVar]:
        return (
            self.the_act
            if phase is Phase.ACT
            else
            self.non_act
        )

    def as_dict(self, phase: Phase) -> EnvVarDict:
        return NameAndValue.as_dict(self.env_vars(phase))

    def defaults_getter_with_values(self, phase: Phase) -> Callable[[], EnvVarDict]:
        return defaults_getter__of_nav(self.env_vars(phase))


def defaults_getter__of_nav(environ: Sequence[NameAndValue]) -> Callable[[], EnvVarDict]:
    def ret_val() -> EnvVarDict:
        return NameAndValue.as_dict(environ)

    return ret_val


class EnvironsSetupForSetBase(EnvironsSetup):
    def with_added(self, phase: Phase, additional: EnvVar) -> List[EnvVar]:
        return self.env_vars(phase) + [additional]

    def with_added__as_dict(self, phase: Phase, additional: EnvVar) -> EnvVarDict:
        return NameAndValue.as_dict(self.with_added(phase, additional))


class EnvironsSetupForUnsetBase(EnvironsSetup):
    def with_removed__as_dict(self, phase: Phase, removed: str) -> EnvVarDict:
        ret_val = self.as_dict(phase)
        del ret_val[removed]
        return ret_val
