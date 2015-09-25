from shellcheck_lib.test_case.instruction.sections.setup import SetupSettingsBuilder


class Assertion:
    def apply(self,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        raise NotImplementedError()


class AnythingGoes(Assertion):
    def apply(self,
              initial: SetupSettingsBuilder,
              actual_result: SetupSettingsBuilder):
        pass
