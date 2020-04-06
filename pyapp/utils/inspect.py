"""
Inspect Utils
~~~~~~~~~~~~~

"""
import importlib
import inspect
from pathlib import Path


def find_root_folder(start_file: Path):
    """
    Find the root package folder from a file within the package
    """
    # Get starting location
    package_path = start_file if start_file.is_dir() else start_file.parent

    # Check current location isn't a path
    if not (package_path / "__init__.py").exists():
        raise ValueError("File not part of a package")

    # Walk up folders to find top level package path
    while (package_path.parent / "__init__.py").exists():
        package_path = package_path.parent

    return package_path


def import_root_module(stack_offset: int = 2):
    """
    Identify and import the root module.
    """
    stack = inspect.stack()
    app_frame = stack[stack_offset]
    package_name = app_frame.frame.f_globals.get("__package__")

    if not package_name:
        # Likely the __main__ module, this module is different and does not contain
        # the package name some assumptions need to be made.
        try:
            root_package = find_root_folder(Path(app_frame.filename)).name
        except ValueError as ex:
            raise RuntimeError(f"Unable to determine root module: {ex}")
    else:
        root_package = package_name.split(".")[0]

    return importlib.import_module(root_package)
