from django.test import TestCase
from django.contrib.auth.models import User


class NimbusTest(TestCase):

    def setUp(self):
        TestCase.setUp(self)
        test = User(username="test")
        test.set_password("test")
        test.save()
        self.client.login(username='test', password='test')

    def _get_url(self, url):
        response = self.client.get(url, follow=True)
        self.failUnlessEqual(response.status_code, 200, 
                             "url=%s %d!=%d" % ( url, 
                                                 response.status_code, 
                                                 200))

    def _get_urls(self, urls):
        for url in urls:
            self._get_url(url)


    def _post_url(self, url, data):
        response = self.client.post(url, data)
        self.failUnlessEqual(response.status_code, 200)





class NimbusViewTest(NimbusTest):

    def test_management(self):
        self._get_urls( ["/management/",
                         "/management/computers/list",
                         "/management/storages/list",
                         "/management/encryptions/list",
                         "/management/strongbox/",
                         "/management/strongbox/umount",
                         "/management/strongbox/changepwd",
                         ])




