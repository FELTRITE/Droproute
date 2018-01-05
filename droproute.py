from termcolor import colored
from tabulate import tabulate
import uuid
import digitalocean

__version__ = "0.1"
__asciiart = """  ____                  ____             _
 |  _ \ _ __ ___  _ __ |  _ \ ___  _   _| |_ ___     ____
 | | | | '__/ _ \| '_ \| |_) / _ \| | | | __/ _ \   /$#</Digital
 | |_| | | | (_) | |_) |  _ < (_) | |_| | ||  __/  /##*/_Ocean
 |____/|_|  \___/| .__/|_| \_\___/ \__,_|\__\___| /___%#@/
                 |_|                                 /#=/
                                                    /_#/
 ver {}                                             /""".format(__version__)


class DropRoute(digitalocean.DigitalOcean):

    def __init__(self):
        super(DropRoute, self).__init__()
        self.uuid = uuid.uuid4().hex
        self.tag = self.uuid
        self.droplet_id = self.uuid.join(["-", "droplet"])
        self.firewall_id = self.uuid.join(["-", "firewall"])
        

    def __availability_color_mapping(self, row):
        if row[0]:
            return [colored(row[1], 'blue'), colored(row[2], 'blue')]
        return [colored(row[1], 'red'), colored(row[2], 'red')]

    def display_available_regions(self):
        response = self.api('get', 'regions')
        regions_json = response['regions']
        # Table headers (4 column list)
        tab_headers = [['','Location', 'Datacenter']]

        # convert from Json to a List (column) of list (row)
        tab_data = [[iter['available'], iter['name'], iter['slug']] for iter in regions_json]

        # termcoloring, converting True/False to Blue/Red colored rows
        colored_tab_data = map(self.__availability_color_mapping, tab_data)

        print(tabulate(tab_headers+colored_tab_data, showindex="always", headers="firstrow"))

    ## -- Assest allocation
    def deploy_droplet(self):
        pass
    def destroy_droplet(self):
        pass
    
    def deploy_firewall(self):
        # deploys a blocking firewall (except ssh)
        pass
    def destroy_firewall(self):
        pass
    
    def deploy_route(self):
        self.deploy_firewall() #First in
        self.deploy_droplet()
         
    def destroy_route(self):
        self.destroy_droplet()
        self.destroy_firewall() #Last out
    
    
    ## -- Assests management
    def update_firewall_rule(self, action, direction, proto, port):
        pass
     
    def deploy_ovpn_server(self):
        pass
    def host_ovpn_client_configuration(self, port):
        self.update_firewall_rule('PUT', 'IN', 'HTTPS', port)
    
    


def main():
    print colored(__asciiart, 'yellow')
    Digimon = DropRoute()
    Digimon.display_available_regions()


if __name__ == '__main__':
    main()
