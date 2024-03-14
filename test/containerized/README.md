Execution of tests in a clean environment, for all supported Python versions.

This is implemented by executing the tests in OCI containers using Docker.
(Obviously, Docker must be installed, and it must be executable by the current user.)

# First, make container images

    $ make images

# Then, run tests towards all supported Python versions

    $ make all

See `Makefile` for details.

# The `run` program

`run` is used to run things in a container designed for executing tests towards a given Python version.
It is used to run the tests, but can also be used to open a shell in a container.

See `run -h` for details.

# Tests of development tools in test/

The `test` subdirectory contains tests of the tools used and implemented in this directory.
These are not executed by the commands above because they should test Exactly
and not the tools used for testing Exactly.
