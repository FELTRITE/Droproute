# -*- coding: utf-8 -*-
import colorama; colorama.init()
from termcolor import colored
from tabulate import tabulate
from random import randint
from config import config
import digitalocean
import base64
import uuid
import time
import os





class DropRoute(digitalocean.DigitalOcean):

    def __init__(self):
        self.UUID = uuid.uuid4().hex[:16]
        super(DropRoute, self).__init__()


    def __initialize_infrastructure(self, datacenter):
        self.tag = "{0}-{1}".format(self.__class__.__name__, self.UUID)
        self.droplet_name = "{0}-{1}".format(self.tag, "droplet")
        self.firewall_name = "{0}-{1}".format(self.tag, "firewall")
        self.online = False
        self.droplet_id = None
        self.droplet_ip = None
        self.firewall_id = None
        self.datacenter = datacenter
        self.datacenter_slug = self.datacenter['slug']


        # Cloudinit Setup
        self.ovpn_client_filename = "{0}_{1}_{2}".format(self.__class__.__name__, self.datacenter_slug, self.UUID)
        self.ovpn_client_filepath = r"ovpn_keys\{filename}.ovpn".format(filename=self.ovpn_client_filename)
        self.ovpn_client_serverport = randint(3000, 6000)
        self.ovpn_client_download_timeout = 300 #5 mins.
        config.CLOUDINIT_SCRIPT = config.CLOUDINIT_SCRIPT.format(ovpn_client_filename=self.ovpn_client_filename,
                                                                 random_server_port=self.ovpn_client_serverport)
        CLOUDINIT_SCRIPT_B64 = base64.b64encode(config.CLOUDINIT_SCRIPT)
        config.CLOUDINIT_USERDATA = config.CLOUDINIT_USERDATA.format(b64_openvpninstall=CLOUDINIT_SCRIPT_B64)

        # Droplet & Firewall configuration
        self.asset_configuration = {
            "FIREWALL_OVPN": config.FIREWALL_OVPN,
            "DROPLET_OVPN": config.DROPLET_OVPN
        }
        self.asset_configuration['DROPLET_OVPN'].update({
            "name": self.droplet_name,
            "tags": [self.tag],
            "user_data": """{}""".format(config.CLOUDINIT_USERDATA)
        })
        self.asset_configuration['FIREWALL_OVPN'].update({
            "name": self.firewall_name,
            "tags": [self.tag]
        })
        for rule in self.asset_configuration['FIREWALL_OVPN']['outbound_rules']:
            if rule['ports'] == 'ovpn_client_serverport':
                rule.update({'ports': self.ovpn_client_serverport})
        for rule in self.asset_configuration['FIREWALL_OVPN']['inbound_rules']:
            if rule['ports'] == 'ovpn_client_serverport':
                rule.update({'ports': self.ovpn_client_serverport})


    def __availability_color_mapping(self, row):
        if row[0]:
            return [colored(row[1], 'blue'), colored(row[2], 'cyan')]
        return [colored(row[1], 'red'), colored(row[2], 'red')]

    def display_available_regions(self):
        print("[+] Displaying available regions")
        regions_json = self.api('get', 'regions')
        regions_list = regions_json['regions']

        # Table headers (4 column list)
        tab_headers = [['', 'Location', 'Datacenter']]

        # convert from Json to a List (column) of list (row)
        tab_data = [[iter['available'], iter['name'].rsplit(' ', 1)[0], iter['slug']] for iter in regions_list]

        # Sort Alphabetically
        tab_data.sort(key=lambda x: x[1]) # sort list by region name
        regions_list = sorted(regions_list)

        # termcoloring, converting True/False to Blue/Red colored rows
        colored_tab_data = map(self.__availability_color_mapping, tab_data)

        print(tabulate(tab_headers+colored_tab_data, showindex="always", headers="firstrow"))
        return regions_list

    def __wait_for_droplet_status(self, resume_status, message=None):
        """
        Wait for
        :param resume_status (string): when desired status is reached, continue.
        """
        if message:
            print message
        #todo: Start animation
        while True:
            response = self.api("GET", "droplets/{}".format(self.droplet_id))
            if response['droplet']['status'] == resume_status:
                #Reached wait trigger! continuing
                #todo: end animation
                break
            time.sleep(config.STATUS_SAMPLEING_INTERVAL)
        # once droplet is deployed
        self.droplet_ip = response['droplet']['networks']['v4'][0]['ip_address']


    # -- Asset allocation
    def create_tag(self):
        self.api("POST", "tags", body={"name": str(self.tag)})

    def delete_tag(self):
        self.api("DELETE", "tags/{uri}".format(uri=self.tag))

    def deploy_droplet(self):
        print "[+] Deploying Droplet {name}".format(name=colored(self.droplet_name, "green"))
        self.asset_configuration['DROPLET_OVPN'].update({
            "region": self.datacenter['slug']
        })
        response = self.api("POST", "droplets", body=self.asset_configuration['DROPLET_OVPN'])
        self.droplet_id = response['droplet']['id']

        # Wait for droplet to finish loading
        self.__wait_for_droplet_status('active', message = "[\] Pending droplet deployment...")

        print "[+] Created Droplet {id}".format(id=colored(self.droplet_id, "green"))

    def destroy_droplet(self):
        self.api("DELETE", "droplets/{uri}".format(uri=self.droplet_id))
        print "[+] Deleted: DROPLET {}".format(colored(self.droplet_name, "red"))

    def deploy_firewall(self):
        print "[+] Deploying Firewall {name}".format(name=colored(self.firewall_name, "green"))
        response = self.api("POST", "firewalls", body=self.asset_configuration['FIREWALL_OVPN'])
        self.firewall_id = response['firewall']['id']
        print "[+] Created Firewall {id}".format(id=colored(self.firewall_id, "green"))

    def destroy_firewall(self):
        self.api("DELETE", "firewalls/{uri}".format(uri=self.firewall_id))
        print "[+] Deleted: FIREWALL {}".format(colored(self.firewall_name, "red"))


    def deploy_Infrastructure(self, datacenter):
        self.__initialize_infrastructure(datacenter)
        print "[+] Selected datacenter: {}".format(colored(self.datacenter['slug'], "cyan"))
        print "[+] Deploying Route Infrastructure {}".format(colored(self.tag, "green"))
        self.create_tag()
        #TODO: Reinstate usage of firewalls...
        # self.deploy_firewall()
        self.deploy_droplet()
        self.online = True
        return True
         
    def destroy_Infrastructure(self):
        print "[+] Decommisioning Route Infrastructure {}".format(colored(self.tag, "red"))
        self.destroy_droplet()
        # self.destroy_firewall()
        self.delete_tag()
        os.remove(self.ovpn_client_filepath)
        self.online = False

    def __download_once_hosted(self, url):
        starttime = time.time()
        print "[\] Waiting for server to host file..."
        while time.time() < starttime + self.ovpn_client_download_timeout:
            try:
                http_data = self.get(url).content
            except:
                http_data = None
                # print "[ ] Still waiting {}".format(time.time() - starttime) #TODO: When implementing Logger, make this LOGLEVEL2
                time.sleep(1)
            if http_data != None:
                print "[+] Downloaded file."
                return http_data
        print "[-] Timed out on download! {} minutes have passed".format(download_timeout/60.0)
        # print "[-] Decommisioning route."
        # self.destroy_Infrastructure()
        return None

    def download_ovpn_key(self):
        base_url = "http://{server_ip}:{serving_port}/{ovpn_client_filename}.ovpn"
        dl_url = base_url.format(server_ip=self.droplet_ip,
                                 serving_port=self.ovpn_client_serverport,
                                 ovpn_client_filename=self.ovpn_client_filename)

        print "[+] Downloading VPN keyfile from `{}`".format(dl_url)
        keyfile_data = self.__download_once_hosted(dl_url)

        if keyfile_data is not None:
            with open(self.ovpn_client_filepath, 'wb') as fh:
                print "[+] Saving file: `{}`".format(self.ovpn_client_filepath)
                fh.write(keyfile_data)


