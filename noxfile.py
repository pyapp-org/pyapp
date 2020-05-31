import nox
from nox.sessions import Session


@nox.session(python=("3.6", "3.7"))
def tests(session: Session):
    session.run("python", "setup.py", "test")
