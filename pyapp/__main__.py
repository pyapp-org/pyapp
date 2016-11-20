import pyapp
from pyapp.cli import CliApplication

app = CliApplication(pyapp)


if __name__ == '__main__':
    app.dispatch()
