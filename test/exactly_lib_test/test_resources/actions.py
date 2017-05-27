def do_nothing(*args, **kwargs):
    pass


def do_return(x):
    def ret_val(*args):
        return x

    return ret_val


def do_raise(ex: Exception):
    def ret_val(*args):
        raise ex

    return ret_val


def action_of(initial_action, action_that_returns):
    if initial_action:
        def complete_action(*args):
            initial_action(*args)
            return action_that_returns(*args)

        return complete_action
    else:
        return action_that_returns
