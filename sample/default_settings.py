from pathlib import Path

here = Path(__file__).parent


FOO_MESSAGE = "Message from foo..."

CHECK_LOCATIONS = ["sample.alt_checks"]

INCLUDE_SETTINGS = [
    f"file://{here}/more-settings.json",
    f"file://{here}/more-settings.yaml",
]
