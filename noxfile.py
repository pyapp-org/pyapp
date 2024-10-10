from pathlib import Path

import nox
from nox.sessions import Session

HERE = Path(__file__).parent


@nox.session(
    python=("python3.10", "python3.11", "python3.12", "python3.13", "pypy3.10"),
    venv_backend=None,
)
def tests(session: Session):
    print(f"🪄 Creating poetry environment for {session.python}")
    session.run("poetry", "env", "use", session.python)

    print("📦 Install dependencies...")
    session.run("poetry", "install", "--with=dev")

    print("▶️ Run tests")
    session.run("poetry", "run", "pytest")
