import nox
from nox.sessions import Session


@nox.session(python=("3.6", "3.7", "3.8"), reuse_venv=True)
def tests(session: Session):
    session.run("poetry", "install")
    session.run("pytest")
