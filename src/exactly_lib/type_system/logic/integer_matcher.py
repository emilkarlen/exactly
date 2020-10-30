from exactly_lib.appl_env.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTrace

IntegerMatcher = MatcherWTrace[int]

IntegerMatcherAdv = ApplicationEnvironmentDependentValue[int]

IntegerMatcherDdv = MatcherDdv[int]

IntegerMatcherSdv = MatcherSdv[int]
