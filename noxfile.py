from pathlib import Path

import nox
from nox.sessions import Session

HERE = Path(__file__).parent


@nox.session(
    python=(
        "python3.10",
        "python3.11",
        "python3.12",
        "python3.13",
        "pypy3.10",
        "python-3.14",
    ),
    venv_backend=None,
)
def tests(session: Session):
    print(f"🪄 Creating poetry environment for {session.python}")
    session.run("poetry", "env", "use", session.python, external=True)

    print("📦 Install dependencies...")
    session.run("poetry", "install", "--with=dev", external=True)

    print("▶️ Run tests")
    session.run(
        "poetry",
        "run",
        "coverage",
        "run",
        "--rcfile=.coveragerc",
        "-m",
        "pytest",
        "--no-cov",
        "--config-file=pytest.ini",
        external=True,
    )
    session.run(
        "poetry",
        "run",
        "coverage",
        "xml",
        "--rcfile=.coveragerc",
        f"-oreports/coverage-{session.python}.xml",
        external=True,
    )
