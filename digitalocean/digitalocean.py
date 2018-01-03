import requests
import json
import os


class DigitalOcean(requests.Session):

    def __init__(self):
        super(DigitalOcean, self).__init__()
        self.access_token = self.__load_credential()
        self.headers.update({'Content-Type': 'application/json',
                             'Authorization':'Bearer {}'.format(self.access_token)
                             })
        self.__api_endpoint = "https://api.digitalocean.com/v2"
        self.account = self.__at_functionality_check()

    def __reset_auth(self, errmsg):
        print errmsg
        access_token = self.__authenticate()
        self.__save_credentials(access_token)
        # Once New authentication is received, we reconstruct the class
        return self.__init__()

    def __authenticate(self):
        #TODO: if yer lazy - Direct user to token web page, else implement access grant flows
        #I know this is shitty
        print "Please refer to https://cloud.digitalocean.com/settings/api/tokens"
        print "And generate a new Access token (call it what ever you want)"
        at = raw_input("--> New Access Token: ")
        return at

    def __save_credentials(self, data):
        cwd = os.path.realpath(__file__)
        fpath = os.path.join(os.path.split(cwd)[0], "Credentials.json")
        jsondata = {"access_token": data}
        with open(fpath, 'wb') as f:
            json.dump(jsondata, f)

    def __load_credential(self):
        cwd = os.path.realpath(__file__)
        fpath = os.path.join(os.path.split(cwd)[0], "Credentials.json")
        try:
            with open(fpath, 'rb') as f:
                data = json.load(f)
        except ValueError:
            return self.__reset_auth("The Available Credential file is corrupted.")

        if not isinstance(data, dict):
            return self.__reset_auth("The Available Credential file is deformated.")

        elif not data.has_key("access_token"):
            return self.__reset_auth("It seems You have yet to supply an Access token.")

        elif len(data['access_token']) != 64:
            return self.__reset_auth("It seems the Access Token available is defected or missing,")

        return data['access_token']

    def api(self, action, uri):
        """
        Handle api requests

        :param uri: Desired endpoint URI (volumes, account, droplets, etc)
        :param action: GET / PUT / DELETE / etc
        :return: json variable with response data
        """
        return self.request(action, "/".join([self.__api_endpoint, uri])).json()

    def __at_functionality_check(self):
        response = self.api('GET', 'account')
        if response.has_key("id"):
            if response['id'] == "forbidden":
                self.__reset_auth("Your Access token does not have proper Permissions.")
            elif response['id'] == "unauthorized":
                self.__reset_auth("Your Access token is no longer valid.")
            return self.__at_functionality_check()
        return response