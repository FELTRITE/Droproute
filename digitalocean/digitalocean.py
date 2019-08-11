import requests
import keyring
import json
import os


class DigitalOcean(requests.Session):

    def __init__(self):
        super(DigitalOcean, self).__init__()
        self.__api_endpoint = "https://api.digitalocean.com/v2"
        self._service = self.__class__.__name__
        self._os_user = os.environ.get('USERNAME')
        self.access_token = self.__load_credential()

        self.headers.update({
            'Content-Type': 'application/json',
            'Authorization':'Bearer {}'.format(self.access_token)
        })
        self.account = self.__get_account_info()


    def __authenticate(self):
        #I know this is shitty
        print "[\] Please refer to https://cloud.digitalocean.com/settings/api/tokens"
        print "[\] And generate a new Access token (call it whatever you want)"
        at = raw_input('[+] DO Access token: ')
        self.__save_credentials(at)

        return at

    def __save_credentials(self, access_token):
        print "[+] Saving {service} credentials for {user}.".format(service=self._service, user=self._os_user)
        keyring.set_password(self._service, self._os_user, access_token)

    def __load_credential(self):
        if self._os_user is None:
            print "[X] There are no {service} credentials for {user}.".format(service=self._service, user=self._os_user)
            self.__authenticate()
            return self.__load_credential()
        print "[+] Loading {service} credentials for {user}.".format(service=self._service, user=self._os_user)
        credential = keyring.get_password(self._service, self._os_user)
        return credential

    def api(self, action, uri, body='{}'):
        """
        Handle api requests

        :param uri: Desired endpoint URI (volumes, account, droplets, etc)
        :param action: GET / PUT / DELETE / etc
        :param body: optional request body
        :return: json variable with response data
        """
        body = json.dumps(body)
        # DELETE requires separate response handling (due to API architecture)
        if action.upper() == "DELETE":
            api_response = self.request("DELETE", "/".join([self.__api_endpoint, uri]))
            if api_response.status_code != 204:

                # weird, maybe its already deleted? trying to list it
                check_response = self.api("GET", uri)
                if check_response.status_code == 404:

                    # ok, all good!
                    return {}
                print "#ERR: Deletion request failed. retrying"
                return self.api("DELETE", uri)

            return {}
        api_response = json.loads(self.request(action, "/".join([self.__api_endpoint, uri]), data=body).content)
        if api_response.has_key('message'):
            raise ValueError("{module}: {msg}".format(
                module="-".join(['#ERR', 'API', uri.upper()]),
                msg=api_response['message'])
            )
        return api_response

    def __get_account_info(self):
        response = self.api('GET', 'account')
        if response.has_key("id"):
            if response['id'] == "forbidden":
                self.__reset_auth("Your Access token does not have proper Permissions.")
            elif response['id'] == "unauthorized":
                self.__reset_auth("Your Access token is no longer valid.")
            return self.__get_account_info()
        return response
