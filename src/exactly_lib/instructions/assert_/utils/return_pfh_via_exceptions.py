from exactly_lib.test_case.phases.result import pfh


class PfhFailException(Exception):
    def __init__(self, err_msg: str):
        super().__init__(err_msg)
        self._err_msg = err_msg

    @property
    def err_msg(self) -> str:
        return self._err_msg


class PfhHardErrorException(Exception):
    def __init__(self, err_msg: str):
        super().__init__(err_msg)
        self._err_msg = err_msg

    @property
    def err_msg(self) -> str:
        return self._err_msg


def translate_pfh_exception_to_pfh(action,
                                   *args, **kwargs) -> pfh.PassOrFailOrHardError:
    try:
        action(*args, **kwargs)
        return pfh.new_pfh_pass()

    except PfhFailException as ex:
        return pfh.new_pfh_fail(ex.err_msg)

    except PfhHardErrorException as ex:
        return pfh.new_pfh_hard_error(ex.err_msg)
