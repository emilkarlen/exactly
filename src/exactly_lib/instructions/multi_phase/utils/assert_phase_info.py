from exactly_lib.test_case.phases.assert_ import WithAssertPhasePurpose, AssertPhasePurpose


class IsAHelperIfInAssertPhase(WithAssertPhasePurpose):
    @property
    def assert_phase_purpose(self) -> AssertPhasePurpose:
        return AssertPhasePurpose.HELPER


class IsBothAssertionAndHelperIfInAssertPhase(WithAssertPhasePurpose):
    @property
    def assert_phase_purpose(self) -> AssertPhasePurpose:
        return AssertPhasePurpose.BOTH
