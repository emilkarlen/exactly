import unittest

from typing import List

from exactly_lib_test.test_resources.process import SubProcessResult


class MainProgramRunner:
    def run(self,
            put: unittest.TestCase,
            arguments: List[str]) -> SubProcessResult:
        raise NotImplementedError()

    def description_for_test_name(self) -> str:
        raise NotImplementedError()

    def __call__(self, put: unittest.TestCase, arguments: List[str]) -> SubProcessResult:
        return self.run(put, arguments)
