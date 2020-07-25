import pathlib
import unittest
from typing import List, Union

from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.logic.program.process_execution import commands as sut
from exactly_lib.type_system.logic.program.process_execution.command import CommandDriver
from exactly_lib_test.type_system.data.test_resources import described_path
from exactly_lib_test.type_system.data.test_resources.described_path import new_primitive


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCommandDriverVisitor),
        unittest.makeSuite(TestCommandDriverArgumentTypePseudoVisitor),
    ]
    )


class TestCommandDriverVisitor(unittest.TestCase):
    def test_visit_shell(self):
        # ARRANGE #
        visitor = _CommandDriverVisitorTestThatRegistersClassOfVisitedObjects('ret-val')
        # ACT #
        ret_val = visitor.visit(sut.CommandDriverForShell('command line'))
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.CommandDriverForShell],
                             'visited classes')

    def test_visit_executable_file(self):
        # ARRANGE #
        visitor = _CommandDriverVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(sut.CommandDriverForExecutableFile(new_primitive(pathlib.Path.cwd())))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.CommandDriverForExecutableFile],
                             'visited classes')

    def test_visit_system_program(self):
        # ARRANGE #
        visitor = _CommandDriverVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(sut.CommandDriverForSystemProgram('pgm'))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.CommandDriverForSystemProgram],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _CommandDriverVisitorTestThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit(_UnknownCommandDriver())


class TestCommandDriverArgumentTypePseudoVisitor(unittest.TestCase):
    def test_visit_shell(self):
        # ARRANGE #
        visitor = _CommandDriverArgumentTypePseudoVisitorThatRegistersClassOfVisitedObjects('ret-val')
        # ACT #
        ret_val = visitor.visit(sut.CommandDriverForShell('command line'))
        # ASSERT #
        self.assertEqual('ret-val', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.CommandDriverForShell],
                             'visited classes')

    def test_visit_executable_file(self):
        # ARRANGE #
        visitor = _CommandDriverArgumentTypePseudoVisitorThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(sut.CommandDriverForExecutableFile(
            described_path.new_primitive(pathlib.Path.cwd()))
        )
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.CommandDriverWithArgumentList],
                             'visited classes')

    def test_visit_system_program(self):
        # ARRANGE #
        visitor = _CommandDriverArgumentTypePseudoVisitorThatRegistersClassOfVisitedObjects('return value')
        # ACT #
        ret_val = visitor.visit(sut.CommandDriverForSystemProgram('pgm'))
        # ASSERT #
        self.assertEqual('return value', ret_val,
                         'Visitor is expected to return value from visit-method')
        self.assertListEqual(visitor.visited_classes,
                             [sut.CommandDriverWithArgumentList],
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

    def visit_shell(self, command_driver: sut.CommandDriverForShell):
        self.visited_classes.append(sut.CommandDriverForShell)
        return self.ret_val

    def visit_executable_file(self, command_driver: sut.CommandDriverForExecutableFile):
        self.visited_classes.append(sut.CommandDriverForExecutableFile)
        return self.ret_val

    def visit_system_program(self, command_driver: sut.CommandDriverForSystemProgram):
        self.visited_classes.append(sut.CommandDriverForSystemProgram)
        return self.ret_val


class _CommandDriverArgumentTypePseudoVisitorThatRegistersClassOfVisitedObjects(
    sut.CommandDriverArgumentTypePseudoVisitor):
    def __init__(self, ret_val):
        self.ret_val = ret_val
        self.visited_classes = []

    def visit_shell(self, command_driver: sut.CommandDriverForShell):
        self.visited_classes.append(sut.CommandDriverForShell)
        return self.ret_val

    def visit_with_argument_list(self, driver: sut.CommandDriverWithArgumentList):
        self.visited_classes.append(sut.CommandDriverWithArgumentList)
        return self.ret_val


class _UnknownCommandDriver(CommandDriver):
    def structure_for(self, arguments: List[str]) -> StructureBuilder:
        raise NotImplementedError('not used')

    def arg_list_or_str_for(self, arguments: List[str]) -> Union[str, List[str]]:
        raise NotImplementedError('not used')
