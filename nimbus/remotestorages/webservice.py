
from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User

import systeminfo
import xmlrpclib
import securexmlrpc
import xmlrpcservicelib


from nimbus.storages.models import Storage
from nimbus.network.models import get_nimbus_address
from nimbus.remotestorages.models import RemoteStorageConf
from nimbus.offsite.models import Offsite


AUTH_TOKEN_FILE="/etc/nimbus/storage.token"
REMOTE_STORAGE_XMLRPC_KEY="/etc/nimbus/storage-xmlrpc.key"
REMOTE_STORAGE_XMLRPC_CERT="/etc/nimbus/storage-xmlrpc.cert"
REMOTE_STORAGE_SERVICE_PORT=settings.REMOTE_STORAGE_SERVICE_PORT #TODO 11111




class RemoteStorageError(Exception):

    def __init__(self, msg, storages):
        self.storages = storages
        super(RemoteStorageError, self).__init__(msg)


class RemoteStorageSyncError(RemoteStorageSyncError):
    pass


class RemoteStorageCommitError(RemoteStorageSyncError):
    pass


class RemoteStorageService(xmlrpcservicelib.SecureService):

    def __init__(self):
        xmlrpcservicelib.SecureService.__init__(self)
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
        return True 

    def get_disk_info(self):
        disk_info = systeminfo.DiskInfo(path=settings.DEFAULT_BACULA_ARCHIVE)
        return disk_info.get_usage()

    def in_transaction(self):
        return transaction.is_managed()

    def enter_transaction(self):
        transaction.enter_transaction_management()
        transaction.managed()
        return True

    def leave_transaction(self):
        transaction.leave_transaction_management()
        return True

    def commit_changes(self):
        transaction.commit()
        return True

    def rollback_changes(self):
        transaction.rollback()
        return True




class RemoteStoragesTransactionManager(object):

    def __init__(self):
        self.remote_storages = self._get_remote_proxies()

    def _get_storages(self):
        return Storage.objects.exclude(address=get_nimbus_address())

    def _get_remote_proxies(self):
        return [ get_remote_storage_interface(s) for s in self._get_storages() ]


    def _call(self, method_name, *args, **kwargs):
        insert_sucesses = set()
        commit_sucesses = set()
        commit_errors = set()
        error = None

        for storage in self.remote_storages:
            try:
                storage.enter_transaction()
                method = getattr(storage, method_name)
                method(*args, **kwargs)
                insert_sucesses.add(storage)
            except xmlrpclib.Fault:
                error = [storage]
                break

        if error:
            for storage in insert_sucesses:
                try:
                    storage.rollback_changes()
                    storage.leave_transaction()
                except xmlrpclib.Fault:
                    pass # rollback fail.
            raise RemoteStorageSyncError("Sync Error", error) #TODO
        else:
            for storage in insert_sucesses:
                try:
                    storage.commit_changes()
                    storage.leave_transaction()
                    commit_sucesses.add(storage)
                except xmlrpclib.Fault:
                    commit_errors.add(storage)
            raise RemoteStorageCommitError("Commit Error", commit_errors) #FUCK!



    def __getattr__(self, attr):
        def call_wrapper(*args, **kwargs):
            return self._call(attr, *args, **kwargs)

        return call_wrapper



def get_remote_storage_interface(storage):
    url = "https://%s:%d" % (storage.address,
                             settings.REMOTE_STORAGE_SERVICE_PORT)
    token = storage.auth_token
    return securexmlrpc.SecureServerProxy(token=token,
                                          uri=url)


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
