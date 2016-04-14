import pathlib
import sys

this_dir = pathlib.Path(sys.path[0])
prj_root_dir_path = this_dir.parent.parent.parent
src_dir_path = prj_root_dir_path / 'src'

# sys.path.insert(0, str(src_dir_path))
from shellcheck_lib.default import shellcheck

shellcheck.main()
