def do_nothing(*args, **kwargs):
    pass


def do_return(x):
    def ret_val(*args, **kwargs):
        return x

    return ret_val


def do_raise(ex: Exception):
    def ret_val(*args, **kwargs):
        raise ex

    return ret_val


def action_of(initial_action, action_that_returns):
    if initial_action:
        def complete_action(*args, **kwargs):
            initial_action(*args, **kwargs)
            return action_that_returns(*args, **kwargs)

        return complete_action
    else:
        return action_that_returns
