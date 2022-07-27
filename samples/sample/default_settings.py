from pathlib import Path

here = Path(__file__).parent


FOO_MESSAGE = "Message from foo..."

CHECK_LOCATIONS = ["sample.alt_checks"]

INCLUDE_SETTINGS = [
    f"file://{here}/more-settings.json",
    f"file://{here}/more-settings.yaml",
    f"file://{here}/more-settings.toml",
]

LOGGING = {
    "formatters": {
        "default": {"format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "default",
            "filename": "out.log",
            "level": "ERROR",
        },
    },
    "loggers": {"pyapp.conf": {"handlers": ["file"]}},
    "root": {
        # 'level' : 'INFO',  # Set from command line arg parser.
        "handlers": ["console"],
    },
}
