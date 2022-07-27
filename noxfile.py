from tempfile import TemporaryDirectory

import nox
from nox.sessions import Session


@nox.session(python=("3.8", "3.9", "3.10"), reuse_venv=True)
def tests(session: Session):
    with TemporaryDirectory() as tmpdir:
        session.install("poetry")
        session.run("poetry", "build")
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            f"--output={tmpdir}/requirements.txt",
        )
        session.install(f"-r{tmpdir}/requirements.txt dist/pytest_pyapp*")
    session.run("pytest")
