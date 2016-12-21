class ActResult:
    def __init__(self,
                 exitcode: int = 0,
                 stdout_contents: str = '',
                 stderr_contents: str = ''):
        self._exitcode = exitcode
        self._stdout_contents = stdout_contents
        self._stderr_contents = stderr_contents

    @property
    def exitcode(self) -> int:
        return self._exitcode

    @property
    def stdout_contents(self) -> str:
        return self._stdout_contents

    @property
    def stderr_contents(self) -> str:
        return self._stderr_contents
