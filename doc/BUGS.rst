BUGS
############################################################

This file should be removed after all mentioned issues are resolved.

When PathPart is absolute THEN PathDdv will be absolute
============================================================

<2018-07-18 wed>

... even if the PathSdv, and maybe also the PathDdv,
say it is relative.

Solution:
Validate that all resolved PathPart:s are relative paths.
