import pathlib
import unittest

from exactly_lib.util.process_execution import commands as sut
from exactly_lib.util.process_execution.command import Command, ProgramAndArguments, CommandDriver


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCommandVisitor),
        unittest.makeSuite(TestCommandDriverVisitor),
    ])


class TestCommandVisitor(unittest.TestCase):
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


class TestCommandDriverVisitor(unittest.TestCase):
    def test_visit_shell(self):
        # ARRANGE #
        visitor = _CommandDriverVisitorTestThatRegistersClassOfVisitedObjects('ret-val')
        # ACT #
        ret_val = visitor.visit(sut.ShellCommandDriver('command line'))
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.ShellCommandDriver],
                             'visited classes')

    def test_visit_executable_file(self):
        # ARRANGE #
        visitor = _CommandDriverVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(sut.ExecutableFileCommandDriver(pathlib.Path.cwd()))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.ExecutableFileCommandDriver],
                             'visited classes')

    def test_visit_system_program(self):
        # ARRANGE #
        visitor = _CommandDriverVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(sut.SystemProgramCommandDriver('pgm'))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.SystemProgramCommandDriver],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _CommandDriverVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(_UnknownCommandDriver())


class _CommandDriverVisitorTestThatRegistersClassOfVisitedObjects(sut.CommandDriverVisitor):
    def __init__(self, ret_val):
        self.ret_val = ret_val
        self.visited_classes = []

    def visit_shell(self, command_driver: sut.ShellCommandDriver):
        self.visited_classes.append(sut.ShellCommandDriver)
        return self.ret_val

    def visit_executable_file(self, command_driver: sut.ExecutableFileCommandDriver):
        self.visited_classes.append(sut.ExecutableFileCommandDriver)
        return self.ret_val

    def visit_system_program(self, command_driver: sut.SystemProgramCommandDriver):
        self.visited_classes.append(sut.SystemProgramCommandDriver)
        return self.ret_val


class _UnknownCommandDriver(CommandDriver):
    pass
