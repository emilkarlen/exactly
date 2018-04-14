import pathlib
import unittest

from exactly_lib.util.process_execution import commands as sut
from exactly_lib.util.process_execution.command import Command, ProgramAndArguments


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestValueVisitor)


class TestValueVisitor(unittest.TestCase):
    def test_visit_shell(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('ret-val')
        # ACT #
        ret_val = visitor.visit(sut.ShellCommand('command line'))
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.ShellCommand],
                             'visited classes')

    def test_visit_executable_file(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(sut.ExecutableFileCommand(pathlib.Path.cwd(), []))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.ExecutableFileCommand],
                             'visited classes')

    def test_visit_system_program(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(sut.SystemProgramCommand(ProgramAndArguments('pgm', [])))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.SystemProgramCommand],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _ValueVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(_UnknownCommand())


class _ValueVisitorTestThatRegistersClassOfVisitedObjects(sut.CommandVisitor):
    def __init__(self, ret_val):
        self.ret_val = ret_val
        self.visited_classes = []

    def visit_shell(self, command: sut.ShellCommand):
        self.visited_classes.append(sut.ShellCommand)
        return self.ret_val

    def visit_executable_file(self, command: sut.ExecutableFileCommand):
        self.visited_classes.append(sut.ExecutableFileCommand)
        return self.ret_val

    def visit_system_program(self, command: sut.SystemProgramCommand):
        self.visited_classes.append(sut.SystemProgramCommand)
        return self.ret_val


class _UnknownCommand(Command):
    @property
    def args(self):
        raise NotImplementedError('not used')

    @property
    def shell(self) -> bool:
        raise NotImplementedError('not used')
