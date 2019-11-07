from pathlib import Path

here = Path(__file__).parent


FOO_MESSAGE: str = "Message from foo..."

CHECK_LOCATIONS: [str] = ["sample.alt_checks"]

INCLUDE_SETTINGS: [str] = [
    f"file://{here}/more-settings.json",
    f"file://{here}/more-settings.yaml",
]
