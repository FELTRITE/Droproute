# -*- coding: utf-8 -*-
from termcolor import colored
from tabulate import tabulate
import animation
import prompter
import uuid
import os
import digitalocean
from config import config

__version__ = "0.1"
UUID = uuid.uuid4().hex


class DropRoute(digitalocean.DigitalOcean):

    def __init__(self):
        global UUID

        super(DropRoute, self).__init__()
        self.tag = UUID
        self.online = False
        self.droplet_id = None
        self.firewall_id = None
        self.datacenter = None
        self.droplet_name = "-".join([self.tag, "droplet"])
        self.firewall_name = "-".join([self.tag, "firewall"])
        self.asset_configuration = {
                        "FIREWALL_BLOCKING": config.FIREWALL_BLOCKING,
                        "FIREWALL_OVPN": config.FIREWALL_OVPN,
                        "DROPLET_OVPN": config.DROPLET_OVPN
        }

        self.asset_configuration['FIREWALL_BLOCKING'].update({
            "name": self.firewall_name,
            "tags": [self.tag]
        })
        self.asset_configuration['FIREWALL_OVPN'].update({
            "name": self.firewall_name,
            "tags": [self.tag]
        })
        self.asset_configuration['DROPLET_OVPN'].update({
            "name": self.droplet_name,
            "tags": [self.tag]
        })

    def __availability_color_mapping(self, row):
        if row[0]:
            return [colored(row[1], 'blue'), colored(row[2], 'cyan')]
        return [colored(row[1], 'red'), colored(row[2], 'red')]

    def display_available_regions(self):
        _loading = animation.Wait(text="[+] Pending API Query ", animation=config.ANIMATION)
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

    # -- Asset allocation
    def create_tag(self):
        self.api("POST", "tags", body={"name": str(self.tag)})
        print "[+] Created: TAG {}".format(self.tag)

    def delete_tag(self):
        self.api("DELETE", "tags/{uri}".format(uri=self.tag))
        print "[+] Deleted: TAG {}".format(colored(self.tag, "red"))

    def deploy_droplet(self):
        print "[+] Deploying Droplet {name}".format(name=colored(self.droplet_name, "green"))
        self.asset_configuration['DROPLET_OVPN'].update({
            "region": self.datacenter['slug']
        })
        response = self.api("POST", "droplets", body=self.asset_configuration['DROPLET_OVPN'])
        self.droplet_id = response['droplet']['id']
        print "[+] Created Droplet {id}".format(id=colored(self.droplet_id, "green"))

    def destroy_droplet(self):
        self.api("DELETE", "droplets/{uri}".format(uri=self.droplet_id))
        print "[+] Deleted: DROPLET {}".format(colored(self.droplet_name, "red"))
    
    def deploy_firewall(self):
        # deploys a blocking firewall (except ssh)
        print "[+] Deploying Firewall {name}".format(name=colored(self.firewall_name, "green"))
        response = self.api("POST", "firewalls", body=self.asset_configuration['FIREWALL_BLOCKING'])
        self.firewall_id = response['firewall']['id']
        print "[+] Created Firewall {id}".format(id=colored(self.firewall_id, "green"))

    def destroy_firewall(self):
        self.api("DELETE", "firewalls/{uri}".format(uri=self.firewall_id))
        print "[+] Deleted: FIREWALL {}".format(colored(self.firewall_name, "red"))

    def update_firewall_rule(self, new_rule):
        # todo writeup, params: action, direction, proto, port
        pass

    def deploy_Infrastructure(self):
        print "[+] Selected datacenter: {}".format(colored(self.datacenter['slug'], "cyan"))
        print "[+] Deploying Route Infrastructure {}".format(colored(self.tag, "green"))
        self.create_tag()
        self.deploy_firewall()  # First in
        self.deploy_droplet()
        self.update_firewall_rule(config.FIREWALL_OVPN)
        self.online = True
        return True
         
    def destroy_Infrastructure(self):
        print "[+] Decommisioning Route Infrastructure {}".format(colored(self.tag, "red"))
        self.destroy_droplet()
        self.destroy_firewall()  # Last out
        self.delete_tag()
        self.online = False


    # -- Asset management
    def deploy_ovpn_server(self):
        pass

    def host_ovpn_client_configuration(self, ):
        self.update_firewall_rule()


def load_client_locally(client_config="/home/derman/client.ovpn"):
    # Todo: load client config to local ovpn bin
    os.system("openvpn --config {clientconfigpath} --ipchange echo yess ".format(clientconfigpath=client_config))
    pass


def prompt_select(display_message, option_list):
    # list --> Chosen selection index
    selection = prompter.prompt(" ".join(["-->",
                                          display_message,
                                          "(1-{})".format(len(option_list)-1),
                                          ":"]))
    if not selection.isdigit() or not len(option_list)> int(selection) >= 0:
        print "#ERR: Supplied an invalid option!"
        return prompt_select(display_message, option_list)
    return int(selection)


def __prompt_route_decommissioning():
    if prompter.yesno("--> Destroy route?", default='no', suffix="\n"):
        # chose to keep
        print "[+] ok."
        return True

    else:
        # chose to destroy
        if not prompter.yesno("--> Are you sure?", default='no', suffix="\n"):
            # chose to destroy, kill
            return False

        print "[+] ok. keeping route up"
        return True


def interactive_mode(Digimon):
    datacenter_list = Digimon.display_available_regions()
    selected_region_index = prompt_select("Select region", datacenter_list)

    Digimon.datacenter = datacenter_list[selected_region_index]
    Digimon.deploy_Infrastructure()


    # todo start heartbeat monitor threading!
    # todo pulse and check droplet to see whether its setup is completed
    _loading = animation.Wait(text='', animation=config.ANIMATION)
    _loading.start()
    load_client_locally()
    while Digimon.online:
        if not __prompt_route_decommissioning():
            # Proceed only when Decommissioning the route
            break
    _loading.stop()
    Digimon.destroy_Infrastructure()


def main():
    print colored(config.asciiart.format(ver=__version__), 'yellow')
    Digimon = DropRoute()
    interactive_mode(Digimon)


if __name__ == '__main__':
    main()
