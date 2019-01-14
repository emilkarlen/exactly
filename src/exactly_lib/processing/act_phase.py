from exactly_lib.test_case.act_phase_handling import ActionToCheckExecutorParser


class ActPhaseSetup(tuple):
    """
    TODO: Believe that the ActionToCheckExecutorParser can completely replace this class
    (since the other members probably will be refactored away)
    """

    def __new__(cls, atc_executor_parser: ActionToCheckExecutorParser):
        return tuple.__new__(cls, (atc_executor_parser,))

    @property
    def atc_executor_parser(self) -> ActionToCheckExecutorParser:
        return self[0]
