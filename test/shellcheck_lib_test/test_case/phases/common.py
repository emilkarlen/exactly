import pathlib
import unittest

from shellcheck_lib.test_case.phases import common as sut


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


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestPhaseLoggingPaths))
    return ret_val


if __name__ == '__main__':
    unittest.main()
