import enum
import unittest

from exactly_lib.test_case import error_description as sut


class ReturnValueEnum(enum.Enum):
    MESSAGE = 1
    EXCEPTION = 2
    EXCEPTION_WITH_MESSAGE = 3
    EXTERNAL_PROCESS = 4


class Visitor(sut.ErrorDescriptionVisitor):
    def _visit_message(self, x: sut.ErrorDescriptionOfMessage):
        return ReturnValueEnum.MESSAGE

    def _visit_exception(self, x: sut.ErrorDescriptionOfException):
        return ReturnValueEnum.EXCEPTION

    def _visit_external_process_error(self, x: sut.ErrorDescriptionOfExternalProcessError):
        return ReturnValueEnum.EXTERNAL_PROCESS


class TestVisitor(unittest.TestCase):
    VISITOR = Visitor()

    def testVisitMessage(self):
        ret_val = self.VISITOR.visit(sut.of_message('message'))
        self.assertIs(ReturnValueEnum.MESSAGE,
                      ret_val)

    def testVisitException(self):
        ret_val = self.VISITOR.visit(sut.of_exception(ValueError()))
        self.assertIs(ReturnValueEnum.EXCEPTION,
                      ret_val)

    def testVisitExternalProcessError(self):
        error = sut.of_external_process_error(1, 'stderr output')
        ret_val = self.VISITOR.visit(error)
        self.assertIs(ReturnValueEnum.EXTERNAL_PROCESS,
                      ret_val)

    def testVisitNonSubClassObject(self):
        with self.assertRaises(ValueError) as info:
            self.VISITOR.visit('string is not a sub class of ErrorDescription')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestVisitor))
    return ret_val


if __name__ == '__main__':
    unittest.main()
