import pathlib
import unittest

from exactly_lib.test_case.phases import common as sut
from exactly_lib.test_case_file_structure import sandbox_directory_structure
from exactly_lib_test.test_resources.execution.tmp_dir import tmp_dir


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestPhaseLoggingPaths))
    ret_val.addTest(unittest.makeSuite(TestPhaseLoggingPathsInstructionFile))
    return ret_val


class TestPhaseLoggingPaths(unittest.TestCase):
    def test_unique_line__sans_tail(self):
        self._check_line_number(5,
                                '',
                                sut.PhaseLoggingPaths.line_number_format.format(5))

    def test_unique_line__with_tail(self):
        self._check_line_number(4,
                                'the-tail',
                                sut.PhaseLoggingPaths.line_number_format.format(4) + '--the-tail')

    def test_duplicated_line__sans_tail(self):
        self._check_line_number(5,
                                '',
                                sut.PhaseLoggingPaths.line_number_format.format(5) + '-2',
                                num_line_number_previously_requested=1)

    def test_duplicated_line__with_tail(self):
        self._check_line_number(5,
                                'the-tail',
                                sut.PhaseLoggingPaths.line_number_format.format(5) + '-3-' + 'the-tail',
                                num_line_number_previously_requested=2)

    def _check_line_number(self,
                           line_number: int,
                           tail: str,
                           expected_line_part: str,
                           num_line_number_previously_requested: int = 0
                           ):
        root_dir = pathlib.Path('root')
        logger = sut.PhaseLoggingPaths(root_dir, 'phase-identifier')
        for i in range(num_line_number_previously_requested):
            logger.for_line(line_number)
        actual = logger.for_line(line_number, tail=tail)
        self.assertEqual(logger.dir_path / expected_line_part,
                         actual)


class TestPhaseLoggingPathsInstructionFile(unittest.TestCase):
    def test_unique_instruction_file(self):
        # ARRANGE #
        root_dir = pathlib.Path('root')
        phase_identifier = 'phase-identifier'
        logger = sut.PhaseLoggingPaths(root_dir, phase_identifier)
        phase_root_dir = sandbox_directory_structure.log_phase_dir(root_dir, phase_identifier)

        for i in range(1, 5):
            expected_base_name = sut.PhaseLoggingPaths.instruction_file_format.format(i)
            expected_path = phase_root_dir / expected_base_name
            # ACT #
            actual_path = logger.unique_instruction_file()
            # ASSERT #
            self.assertEqual(expected_path,
                             actual_path)

    def test_unique_instruction_file_as_existing_dir(self):
        # ARRANGE #
        with tmp_dir() as root_dir:
            phase_identifier = 'phase-identifier'
            logger = sut.PhaseLoggingPaths(root_dir, phase_identifier)

            expected_phase_root_dir = sandbox_directory_structure.log_phase_dir(root_dir, phase_identifier)
            expected_base_name = sut.PhaseLoggingPaths.instruction_file_format.format(1)
            expected_path = expected_phase_root_dir / expected_base_name

            # ACT #
            instruction_dir = logger.unique_instruction_file_as_existing_dir()
            # ASSERT #
            self.assertEqual(expected_path,
                             instruction_dir)
            self.assertTrue(instruction_dir.is_dir(),
                            'the instruction directory should exist and be a directory')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
