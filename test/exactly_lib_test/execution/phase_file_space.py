import pathlib
import unittest

from exactly_lib.execution import phase_file_space as sut
from exactly_lib.test_case import phase_identifier
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources.files import tmp_dir


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_phase(self):
        # ARRANGE #
        with tmp_dir.tmp_dir() as root_dir:
            factory = sut.PhaseTmpFileSpaceFactory(root_dir)
            cases = [
                NameAndValue(
                    phase_identifier.ASSERT.identifier,
                    phase_identifier.ASSERT,
                ),
                NameAndValue(
                    phase_identifier.ACT.identifier,
                    phase_identifier.ACT,
                ),
            ]
            for case in cases:
                with self.subTest(case.name):
                    expected_dir = root_dir / _expected_phase_dir(case.value)
                    # ACT & ASSERT #
                    _check(
                        self,
                        expected_dir,
                        factory.for_phase__main(case.value),
                    )

    def test_instruction_main_step(self):
        # ARRANGE #
        with tmp_dir.tmp_dir() as root_dir:
            factory = sut.PhaseTmpFileSpaceFactory(root_dir)
            cases = [
                NameAndValue(
                    phase_identifier.ASSERT.identifier,
                    (phase_identifier.ASSERT, 1)
                ),
                NameAndValue(
                    phase_identifier.ASSERT.identifier,
                    (phase_identifier.ASSERT, 5)
                ),
                NameAndValue(
                    phase_identifier.SETUP.identifier,
                    (phase_identifier.SETUP, 2),
                ),
            ]
            for case in cases:
                with self.subTest(case.name):
                    expected_dir = (
                            root_dir /
                            _expected_phase_dir(case.value[0]) /
                            _expected_instruction_dir(case.value[1])
                    )
                    # ACT & ASSERT #
                    _check(
                        self,
                        expected_dir,
                        factory.instruction__main(case.value[0], case.value[1]),
                    )

    def test_instruction_validation_step(self):
        # ARRANGE #
        with tmp_dir.tmp_dir() as root_dir:
            factory = sut.PhaseTmpFileSpaceFactory(root_dir)
            cases = [
                NameAndValue(
                    phase_identifier.BEFORE_ASSERT.identifier,
                    (phase_identifier.BEFORE_ASSERT, 1)
                ),
                NameAndValue(
                    phase_identifier.CLEANUP.identifier,
                    (phase_identifier.CLEANUP, 2)
                ),
                NameAndValue(
                    phase_identifier.SETUP.identifier,
                    (phase_identifier.SETUP, 2),
                ),
            ]
            for case in cases:
                with self.subTest(case.name):
                    expected_dir = (
                            root_dir /
                            sut.PhaseTmpFileSpaceFactory.VALIDATION_SUB_DIR /
                            _expected_phase_dir(case.value[0]) /
                            _expected_instruction_dir(case.value[1])
                    )
                    # ACT & ASSERT #
                    _check(
                        self,
                        expected_dir,
                        factory.instruction__validation(case.value[0], case.value[1]),
                    )


def _check(put: unittest.TestCase,
           expected_space_root_dir: pathlib.Path,
           actual_storage: sut.TmpFileStorage,
           ):
    storage_root_dir__may_not_exist = actual_storage.root_dir__may_not_exist
    put.assertEqual(expected_space_root_dir, storage_root_dir__may_not_exist)

    put.assertFalse(storage_root_dir__may_not_exist.exists(),
                    'space root dir should not exist directly after storage creation')
    storage_dir__existing = actual_storage.root_dir__existing
    put.assertTrue(storage_dir__existing.is_dir(),
                   'space root dir should be created when accessed')
    put.assertEqual(storage_root_dir__may_not_exist,
                    storage_dir__existing,
                    'Dirs should be the same - regardless of accessed via _may_not_exist or __existing')
    fst_path = actual_storage.paths_access.new_path()
    snd_path = actual_storage.paths_access.new_path()
    storage_root_dir = storage_root_dir__may_not_exist
    put.assertEqual(storage_root_dir / _expected_path_in_space(1),
                    fst_path,
                    '1st path in space')
    put.assertEqual(storage_root_dir / _expected_path_in_space(2),
                    snd_path,
                    '2nd path in space')


def _expected_phase_dir(phase: phase_identifier.Phase) -> str:
    return '-'.join((
        str(phase.the_enum.value),
        phase.identifier,
    ))


def _expected_instruction_dir(instruction_number: int) -> str:
    return str(instruction_number).zfill(3)


def _expected_path_in_space(path_number: int) -> str:
    return str(path_number).zfill(2)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
