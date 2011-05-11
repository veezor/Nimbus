import nimbusclientlib


AUTH_TOKEN_FILE="/etc/nimbus/storage.token"

class RemoteStorageNotifier(nimbusclientlib.Notifier):
    ACTION_URL = "http://%s:%d/storages/new/"
    LOGIN_URL = "http://%s:%d/session/login/"
    TOKEN_FILE = AUTH_TOKEN_FILE


