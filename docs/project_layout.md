TASKR
-----------------------

* The indented file is imported by the one above it.

__main__.py 

    cli.py 

        errors.py
        models.py (dataclasses, datetime, enum)

Notes: The `__init__.py` file is not included in this diagram because it has no dependencies on any other files. This file simply informs Python that "this is a package, not a layer."

    __main__.py acts as a shell because it has a single entry path, whereas cli.py is a layer because all entry paths lead to it.

