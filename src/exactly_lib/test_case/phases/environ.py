from typing import Callable, Dict, Optional

EnvVarsDict = Dict[str, str]

OptionalEnvVarsDict = Optional[EnvVarsDict]

DefaultEnvironGetter = Callable[[], EnvVarsDict]
