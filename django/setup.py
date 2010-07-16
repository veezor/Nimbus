from cx_Freeze import setup, Executable



import sys
sys.path.append("../libs/")





setup(
        name = "Nimbus",
        version = "0.1",
        description = "Nimbus Backup",
        executables = [ Executable("nimbus.py", targetName="nimbus.fcgi")],
        options = { "build_exe": 
                      { "compressed" :  True,
                        "build_exe" : "binary",
                        "silent" : True,
                        "optimize" :  "1", 
                        "create_shared_zip" :  False,
                        "include_in_shared_zip" : False,   
                        "append_script_to_exe" :  True,
                        "packages": [ "pybacula",
                                      "networkutils",
                                      "bconsole",
                                      "keymanager",
                                      "encryptdevicemanager",
                                      "backup_corporativo"],
                        "includes" : [ "backup_corporativo.bkp.views",
                                       "backup_corporativo.bkp.templatetags.bkp_extras",
                                       "backup_corporativo.bkp.tests"],
                        "zip_includes" : [ ("backup_corporativo/templates/", "backup_corporativo/bkp/templates/") ],
                        "excludes" : ["email","PIL","flup","django", "xml", "pytz"],
                        "include_files" : [ ("backup_corporativo/static", "static" )] }}
)
