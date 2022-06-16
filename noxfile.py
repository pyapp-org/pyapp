import nox
from nox.sessions import Session


@nox.session(python=("3.8", "3.9", "3.10"), reuse_venv=True)
def tests(session: Session):
    session.install("poetry")
    session.run("poetry", "install")
    session.run("pytest")
