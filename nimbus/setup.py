from cx_Freeze import setup, Executable



import sys
import os
from os.path import join, dirname, walk, exists


sys.path.append( join( dirname(__file__), '..'))
sys.path.append( join( dirname(__file__), '..', 'libs'))

from nimbus import settings

packages = [ "pybacula",
             "networkutils",
             "keymanager",
             "encryptdevicemanager",
             "nimbus",
             "nimbus.settings",
             "nimbus.shared",
             "nimbus.libs"]



def has_templates(name):
    appname = name.split('.')[-1]
    template_dir = join(appname, 'templates')
    return exists(template_dir)

def get_template_dir(name):
    nimbus, appname = name.split('.')
    fdir = join(appname, 'templates')
    fulldir = join(nimbus, appname, 'templates')
    return fdir, fulldir


nimbus_apps = [  app for app in settings.INSTALLED_APPS if app.startswith('nimbus') ]
packages.extend( nimbus_apps )
templates_dir = [ get_template_dir(app) for app in nimbus_apps if has_templates(app) ]


setup(
        name = "Nimbus",
        version = "1.0",
        description = "Nimbus Cloud Backup",
        executables = [ Executable("main.py", targetName="nimbus")],
        options = { "build_exe":
                      { "compressed" :  True,
                        "build_exe" : "binary",
                        "silent" : True,
                        "optimize" :  "1",
                        "create_shared_zip" :  True,
                        "include_in_shared_zip" : False,
                        "append_script_to_exe" :  True,
                        "packages": packages,
                        "excludes" : ["email","PIL","django", "xml", "pytz", "gunicorn", "distutils", "json"],
                        "zip_includes" : templates_dir,
                        "include_files" : [ ("media", "media" )],
                      }
        }
)
