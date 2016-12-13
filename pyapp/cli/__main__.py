import pyapp
from pyapp.app import CliApplication

app = CliApplication(
    pyapp,
    name='pyapp',
    application_settings='pyapp.default_settings'
)


if __name__ == '__main__':
    app.dispatch()
