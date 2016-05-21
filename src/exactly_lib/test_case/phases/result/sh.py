class SuccessOrHardError(tuple):
    """
    Represents EITHER success OR hard error.
    """

    def __new__(cls,
                failure_message: str):
        return tuple.__new__(cls, (failure_message,))

    @property
    def failure_message(self) -> str:
        """
        :return None iff the object represents SUCCESS.
        """
        return self[0]

    @property
    def is_success(self) -> bool:
        return self[0] is None

    @property
    def is_hard_error(self) -> bool:
        return not self.is_success

    def __str__(self):
        if self.is_success:
            return 'SUCCESS'
        else:
            return 'FAILURE:{}'.format(self.failure_message)


def new_sh_success() -> SuccessOrHardError:
    return __SH_SUCCESS


def new_sh_hard_error(failure_message: str) -> SuccessOrHardError:
    if failure_message is None:
        raise ValueError('A HARD ERROR must have a failure message (that is not None)')
    return SuccessOrHardError(failure_message)


__SH_SUCCESS = SuccessOrHardError(None)
