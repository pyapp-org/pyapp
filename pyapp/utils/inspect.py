import importlib
import inspect

from pathlib import Path


def find_root_folder(start_file: Path):
    """
    Find the root package folder from a file within the package
    """
    package_path = start_file.parent
    
    # Walk up folders to find top level package path
    while (package_path.parent / "__init__.py").exists():
        package_path = package_path.parent
    
    if not (package_path / "__init__.py").exists():
        raise ValueError("File not part of a packge")
    
    return package_path       


def determine_root_module(stack_offset: int = 2):
    """
    Determine namespace root from an object instance
    """
    stack = inspect.stack()
    app_frame = stack[stack_offset]
    package_name = app_frame.frame.f_globals.get("__package__")

    if not package_name:
        # Likely the __main__ module, this module is different and does not contain
        # the package name some assumptions need to be made.
        try:
            root_package = find_root_folder(Path(app_frame.filename)).name
        except ValueError:
            raise RuntimeError("Not able to determine root module.")
    else:
        root_package = package_name.split(".")[0]

    try:
        return importlib.import_module(root_package)
    except ImportError:
        raise RuntimeError("Not able to determine root module.")
