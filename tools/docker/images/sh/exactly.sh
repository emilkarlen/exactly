alias xly="python ${XLY_REPO_COPY_DIR}/src/default-main-program-runner.py"

alias cde="cd ${XLY_REPO_COPY_DIR}"

set_xly_py_path() { # PRJ-ROOT-DIR
  if [ "${1}" == '-h' ]; then
    echo "Sets PYTHONPATH for Exactly source dirs to given EXACTLY-PRJ-ROOT-DIR"
    return 0
  fi
  if [ $# -ne 1 ]; then
    echo "Usage: EXACTLY-PRJ-ROOT-DIR"
    return 0
  fi
  if [ ! -d "${1}" ]; then
    echo "Not a dir: $1" >&2
    return 1
  fi

  local REPO_ROOT_DIR=$(
    cd $1
    pwd -P
  )
  local ADDITIONAL_PY_PATHS="${REPO_ROOT_DIR}/src:${REPO_ROOT_DIR}/test"

  if [ ${PYTHONPATH} ]; then
    export PYTHONPATH=${ADDITIONAL_PY_PATHS}:${PYTHONPATH}
  else
    export PYTHONPATH=${ADDITIONAL_PY_PATHS}
  fi
}
