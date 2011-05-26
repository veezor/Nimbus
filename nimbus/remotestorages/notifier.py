import urllib
import simplejson


import nimbusclientlib

from nimbus.config.models import Config

AUTH_TOKEN_FILE="/etc/nimbus/storage.token"

class NewRemoteStorageNotifier(nimbusclientlib.Notifier):
    ACTION_URL = "http://%s:%d/storages/new/"
    LOGIN_URL = "http://%s:%d/session/login/"
    TOKEN_FILE = AUTH_TOKEN_FILE


    def get_post_data(self, storage):
        args = dict(password=storage.password,
                    name=storage.name)
        return urllib.urlencode(args.items())


    def notify(self, storage):
        self.login()
        handle = self.urlopener.open( self.get_url(self.ACTION_URL),
                                      self.get_post_data(storage) )
        data = handle.read()
        handle.close()

        data = simplejson.loads(data)

        config = Config.get_instance()
        config.director_name = data['director_name']
        config.save()

        token = data['token']
        self.save_auth_token(token)




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







