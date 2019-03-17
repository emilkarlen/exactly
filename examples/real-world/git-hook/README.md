Test a git hook that prepares the commit message.

The hook should prepend an issue number to the commit message,
if it does not have one.

The issue number should be taken from the name of the current branch

### Setup

The source code of the hook is `examples/executables-src/prepare-commit-msg.py`.

See `examples/README` for instructions on how to build it.
