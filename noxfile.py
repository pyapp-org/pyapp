import nox
from nox.sessions import Session


@nox.session(python=("3.6", "3.7", "3.8", "3.9"), reuse_venv=True)
def tests(session: Session):
    session.install("poetry")
    session.run("poetry", "install")
    session.run("pytest")
