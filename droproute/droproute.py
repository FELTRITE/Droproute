
class DropRoute():

    def __init__(self):
        self.access_token = self.__load_credential()
        self.api = requests.Session()
        self.api.headers.update({'Content-Type': 'application/json',
                                 'Authorization':'Bearer {}'.format(self.access_token)
                                 })

    def __authenticate(self):
        #TODO: if yer lazy - Direct user to token web page, else implement access grant flows
        pass

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

        if data.has_key("access_token") == False:
            access_token = self.__authenticate()
            self.__save_credentials(access_token)
            return access_token
        return data['access_token']


