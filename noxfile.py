from pathlib import Path

import nox
from nox.sessions import Session

HERE = Path(__file__).parent


@nox.session(python=("3.10", "3.11", "3.12", "3.13"), venv_backend=None)
def tests(session: Session):
    print(f"🪄 Creating poetry environment for {session.python}")
    session.run("poetry", "env", "use", f"python{session.python}")

    print("📦 Install dependencies...")
    session.run("poetry", "install", "--with=dev")

    print("▶️ Run tests")
    session.run("poetry", "run", "pytest")
