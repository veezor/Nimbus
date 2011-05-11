

from django.conf import settings
from django.contrib.auth.models import User

import systeminfo
import securexmlrpc
import xmlrpcservicelib



from nimbus.remotestorages.models import RemoteStorageConf
from nimbus.offsite.models import Offsite


AUTH_TOKEN_FILE="/etc/nimbus/storage.token"
REMOTE_STORAGE_XMLRPC_KEY="/etc/nimbus/storage-xmlrpc.key"
REMOTE_STORAGE_XMLRPC_CERT="/etc/nimbus/storage-xmlrpc.cert"
REMOTE_STORAGE_SERVICE_PORT=settings.REMOTE_STORAGE_SERVICE_PORT #TODO 11111


class RemoteStorageService(xmlrpcservicelib.SecureService):

    def __init__(self):
        self.auth_token_file = AUTH_TOKEN_FILE


    def set_disk_alert_thresholds(self, warning, critical):
        conf = RemoteStorageConf.get_instance()
        conf.disk_warning_threshold = warning
        conf.disk_critical_threshold = critical
        conf.save()
        return True


    def enable_managed_mode(self):
        conf = RemoteStorageConf.get_instance()
        conf.set_managed_mode()
        conf.save()
        return True


    def disable_managed_mode(self):
        conf = RemoteStorageConf.get_instance()
        conf.set_standalone_mode()
        conf.save()

        offsite_conf = Offsite.get_instance()
        offsite_conf.active = False
        offsite_conf.save()
        return True


    def set_user_password(self, password):
        user = User.objects.get(id=1)
        user.password = password
        user.save()
        return True


    def set_offsite_conf(self, access_key, secret_key, rate_limit, active):
        offsite_conf = Offsite.get_instance()
        offsite_conf.access_key = access_key
        offsite_conf.secret_key = secret_key
        offsite_conf.rate_limit = rate_limit
        offsite_conf.active = active
        offsite_conf.save()
        return True


    def check_status(self):
        return True #TODO: verify bacula-sd status

    def get_disk_info(self):
        disk_info = systeminfo.DiskInfo(path=settings.DEFAULT_BACULA_ARCHIVE)
        return disk_info.get_usage()



def get_remote_storage_xmlrpc_server():
    server = securexmlrpc.secure_xmlrpc(REMOTE_STORAGE_XMLRPC_KEY,
                                        REMOTE_STORAGE_XMLRPC_CERT,
                                        ('',REMOTE_STORAGE_SERVICE_PORT),
                                        settings.NIMBUS_SSLCONFIG)
    server.register_instance(RemoteStorageService())
    return server



def main():
    server = get_remote_storage_xmlrpc_server()
    server.serve_forever()



if __name__ == "__main__":
    main()
