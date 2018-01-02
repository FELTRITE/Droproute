import requests
import json
import os


class DropRoute(requests.Session):

    def __init__(self):
        super(DropRoute, self).__init__()
        self.access_token = self.__load_credential()
        self.headers.update({'Content-Type': 'application/json',
                             'Authorization':'Bearer {}'.format(self.access_token)
                             })
        self.__api_endpoint = "https://api.digitalocean.com/v2"
        self.account = self.api('GET', 'account')



    def __authenticate(self):
        #TODO: if yer lazy - Direct user to token web page, else implement access grant flows
        #I know this is shitty
        print "It seems You have yet to supply an Access token"
        print "Please refer to https://cloud.digitalocean.com/settings/api/tokens"
        print "And generate a new Access token (call it what ever you want)"
        at = raw_input("--> New Access Token: ")
        return at

    def __save_credentials(self, data):
        cwd = os.path.realpath(__file__)
        fpath = os.path.join(os.path.split(cwd)[0], "Credentials.json")
        with open(fpath, 'wb') as f:
            json.dump(data, f)

    def __load_credential(self):
        cwd = os.path.realpath(__file__)
        fpath = os.path.join(os.path.split(cwd)[0], "Credentials.json")
        with open(fpath, 'rb') as f:
            data = json.load(f)

        if not data.has_key("access_token"):
            access_token = self.__authenticate()
            self.__save_credentials(access_token)
            return access_token
        return data['access_token']

    def api(self, action, uri):
        """
        Handle api requests

        :param uri: Desired endpoint URI (Volumes, Account)
        :param action: GET / PUT / DELETE / etc
        :return: json variable with respnse data
        """
        return self.request(action, "/".join([self.__api_endpoint, uri])).json()
