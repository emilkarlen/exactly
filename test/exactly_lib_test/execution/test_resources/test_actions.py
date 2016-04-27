from exactly_lib.test_case.phases.result import svh


def validate_action_that_returns(ret_val: svh.SuccessOrValidationErrorOrHardError):
    def f():
        return ret_val

    return f


def validate_action_that_raises(ex: Exception):
    def f():
        raise ex

    return f


def execute_action_that_does_nothing():
    def f():
        pass

    return f


def execute_action_that_raises(ex: Exception):
    def f():
        raise ex

    return f
