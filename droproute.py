# -*- coding: utf-8 -*-
from termcolor import colored
from tabulate import tabulate
import animation
import uuid
import digitalocean
import config


__version__ = "0.1"

UUID = uuid.uuid4().hex

class DropRoute(digitalocean.DigitalOcean):

    def __init__(self):
        global UUID

        super(DropRoute, self).__init__()
        self.tag = "qwert123456"#UUID
        self.droplet_id = ""
        self.firewall_id = ""
        self.droplet_name = "-".join([self.tag, "droplet"])
        self.firewall_name = "-".join([self.tag, "firewall"])



    def __availability_color_mapping(self, row):
        if row[0]:
            return [colored(row[1], 'blue'), colored(row[2], 'cyan')]
        return [colored(row[1], 'red'), colored(row[2], 'red')]

    def display_available_regions(self):
        _loading = animation.Wait(text="[+] Pending API Query", animation="bar")
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
    def create_tag(self):
        #todo writeup
        pass

    def delete_tag(self):
        self.api("DELETE", "tags/{uri}".format(uri=self.tag))
        print "[+] Deleted: TAG {}".format(colored(self.tag, "red"))
        return

    def deploy_droplet(self):
        #todo writeup, implement creation validation!
        pass

    def destroy_droplet(self):
        self.api("DELETE", "droplets/{uri}".format(uri=self.droplet_id))
        print "[+] Deleted: DROPLET {}".format(colored(self.droplet_name, "red"))
        return
    
    def deploy_firewall(self):
        # deploys a blocking firewall (except ssh)
        #todo writeup, implement creation validation!
        pass

    def destroy_firewall(self):
        self.api("DELETE", "firewalls/{uri}".format(uri=self.firewall_id))
        print "[+] Deleted: FIREWALL {}".format(colored(self.firewall_name, "red"))
        return


    def deploy_route(self, selected_datacenter):
        _loading = animation.Wait(text='', animation=config.ANIMATION)
        _loading.start()
        print "[+] Selected datacenter: {}".format(colored(selected_datacenter['slug'], "cyan"))

        self.creat_tag()
        self.deploy_firewall() #First in
        self.deploy_droplet()
        self.update_firewall_rule()


        import time; time.sleep(10) #todo remove this
        print "[+] Done!"
        _loading.stop()
        return True
         
    def destroy_route(self):
        #todo writeup
        self.destroy_droplet()
        self.destroy_firewall() #Last out
        self.delete_tag()
    
    
    ## -- Assest management
    def update_firewall_rule(self):
        #todo writeup, params: action, direction, proto, port
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
    print colored(config.asciiart.format(ver=__version__), 'yellow')
    Digimon = DropRoute()
    datacenter_list = Digimon.display_available_regions()
    selected_region_index = prompt_select("Select region", datacenter_list)

    Digimon.delete_tag()
    Digimon.deploy_route(datacenter_list[selected_region_index])


if __name__ == '__main__':
    main()
