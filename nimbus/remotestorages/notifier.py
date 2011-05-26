import nimbusclientlib


AUTH_TOKEN_FILE="/etc/nimbus/storage.token"

class RemoteStorageNotifier(nimbusclientlib.Notifier):
    ACTION_URL = "http://%s:%d/storages/new/"
    LOGIN_URL = "http://%s:%d/session/login/"
    TOKEN_FILE = AUTH_TOKEN_FILE




class DiskWarnningNotifier(nimbusclientlib.Notifier):
    ACTION_URL = "http://%s:%d/remotestorages/warnning_alert/"



    def notify(self):
        self.login()
        handle = self.urlopener.open( self.get_url(self.ACTION_URL),
                                      self.get_post_data() )
        data = handle.read()
        handle.close()



class DiskCriticalNotifier(DiskWarnningNotifier):
    ACTION_URL = "http://%s:%d/remotestorages/critical_alert/"







