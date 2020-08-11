readonly DOCKER_IMAGE_PREFIX='alpine-py'

############################################################
# Must be in sync with docker container
#
# See Dockerfile
############################################################

readonly NON_ROOT_USER='tester'

readonly CONTAINER__REPO_ROOT=/exactly/mounted-repo
readonly CONTAINER__SHARE_DIR=/share
readonly CONTAINER__WORK_DIR=/workdir
readonly CONTAINER__VENV_DIR=/workdir/venv

readonly ACTION__TEST__COMMAND='copy-and-test-repo'
readonly ACTION__TEST_W_INSTALL__COMMAND='copy-and-test-repo --venv'
