from cx_Freeze import setup, Executable
import sys


sys.path.extend(["/var/nimbus/hg/libs/","/var/nimbus/hg/django/"])



setup(
        name = "Nimbus",
        version = "0.1",
        description = "Nimbus Backup",
        executables = [ Executable("nimbus.py", targetName="nimbus.fcgi")],
        options = { "build_exe": 
                      { "compressed" :  True, 
                        "silent" : True,
                        "optimize" :  "1", 
                        "create_shared_zip" :  False,
                        "include_in_shared_zip" : False,   
                        "append_script_to_exe" :  True,
                        "includes": [ "pybacula",
                                      "bconsole",
                                      "networkutils",
                                      "keymanager",
                                      "truecrypt",
                                      "backup_corporativo.settings",
                                      "backup_corporativo.bkp.views",
                                      "backup_corporativo.bkp.templatetags.bkp_extras",
                                      "backup_corporativo.urls"],
                        "excludes" : ["email","django","flup"],
                        "include_files" : [(".htaccess", ".htaccess"), 
                                           ("/var/nimbus/hg/django/backup_corporativo/templates/bkp/static", "static" )] }}
)
