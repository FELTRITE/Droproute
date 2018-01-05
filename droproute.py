# -*- coding: utf-8 -*-
from termcolor import colored
from tabulate import tabulate
import animation
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

PULSE_ANIMATION = (
    '[-------]', '[⌃------]', '[⌄^-----]', '[-⌄^----]', '[--⌄^---]',
    '[---⌄^--]', '[----⌄^-]', '[-----⌄^]', '[------⌄]', '[-------]'
)

UUID = uuid.uuid4().hex

class DropRoute(digitalocean.DigitalOcean):

    def __init__(self):
        global UUID

        super(DropRoute, self).__init__()
        self.tag = UUID
        self.droplet_id = "-".join([self.tag, "droplet"])
        self.firewall_id = "-".join([self.tag, "firewall"])


    def __availability_color_mapping(self, row):
        if row[0]:
            return [colored(row[1], 'blue'), colored(row[2], 'cyan')]
        return [colored(row[1], 'red'), colored(row[2], 'red')]

    def display_available_regions(self):
        _loading = animation.Wait(text="Pending API Query", animation="bar")
        _loading.start()
        regions_json = self.api('get', 'regions')
        regions_list = regions_json['regions']

        # Table headers (4 column list)
        tab_headers = [['', 'Location', 'Datacenter']]

        # convert from Json to a List (column) of list (row)
        tab_data = [[iter['available'], iter['name'].rsplit(' ', 1)[0], iter['slug']] for iter in regions_list]

        # termcoloring, converting True/False to Blue/Red colored rows
        colored_tab_data = map(self.__availability_color_mapping, tab_data)

        _loading.stop()
        print(tabulate(tab_headers+colored_tab_data, showindex="always", headers="firstrow"))
        return regions_list


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

    def deploy_route(self, selected_datacenter):
        _loading = animation.Wait(animation=PULSE_ANIMATION)
        _loading.start()
        print "[+] Selected datacenter: {}".format(colored(selected_datacenter['slug'], "cyan"))

        self.deploy_firewall() #First in
        self.deploy_droplet()
        import time; time.sleep(10) #todo remove this
        print "[+] Done!"
        _loading.stop()
        return True
         
    def destroy_route(self):
        self.destroy_droplet()
        self.destroy_firewall() #Last out
    
    
    ## -- Assest management
    def update_firewall_rule(self, action, direction, proto, port):
        pass
     
    def deploy_ovpn_server(self):
        pass
    def host_ovpn_client_configuration(self, port):
        self.update_firewall_rule('PUT', 'IN', 'HTTPS', port)




    
def load_client_locally(client_config):
    #Todo: load client config to local ovpn bin
    pass

def prompt_select(display_message, option_list):
    # list --> Chosen selection index
    selection = raw_input(" ".join(["-->",
                                    display_message,
                                    "(1-{})".format(len(option_list)-1),
                                    ":"]))
    if not selection.isdigit() or not len(option_list)> int(selection) >= 0:
        print "#ERR: Supplied an invalid option!"
        return prompt_select(display_message, option_list)
    return int(selection)

def main():
    print colored(__asciiart, 'yellow')
    Digimon = DropRoute()
    datacenter_list = Digimon.display_available_regions()
    selected_region_index = prompt_select("Select region", datacenter_list)

    Digimon.deploy_route(datacenter_list[selected_region_index])


if __name__ == '__main__':
    main()