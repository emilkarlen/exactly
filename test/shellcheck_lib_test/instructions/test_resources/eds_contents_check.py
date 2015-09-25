import unittest

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure


class Assertion:
    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        raise NotImplementedError()


class AnythingGoes(Assertion):
    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        pass


class UnconditionalFail(Assertion):
    def apply(self,
              put: unittest.TestCase,
              eds: ExecutionDirectoryStructure):
        put.fail('Unconditional fail')
