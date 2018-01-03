from termcolor import colored
from tabulate import tabulate
import digitalocean


__asciiart = """  ____                  ____             _
 |  _ \ _ __ ___  _ __ |  _ \ ___  _   _| |_ ___     ____
 | | | | '__/ _ \| '_ \| |_) / _ \| | | | __/ _ \   /$#</Digital
 | |_| | | | (_) | |_) |  _ < (_) | |_| | ||  __/  /##*/_Ocean
 |____/|_|  \___/| .__/|_| \_\___/ \__,_|\__\___| /___%#@/
                 |_|                                 /#=/
                                                    /_#/
 ver {}                                             /""".format("0.1")


class DropRoute(digitalocean.DigitalOcean):

    def __init__(self):
        super(DropRoute, self).__init__()

    def __availability_color_mapping(self, row):
        if row[0]:
            return [colored(row[1], 'blue'), colored(row[2], 'blue')]
        return [colored(row[1], 'red'), colored(row[2], 'red')]

    def display_available_regions(self):
        response = self.api('get', 'regions')
        regions = response['regions']
        # Table headers (4 column list)
        tab_headers = [['','Location', 'Datacenter']]

        # convert from Json to a List (column) of list (row)
        tab_data = [[iter['available'], iter['name'], iter['slug']] for iter in regions]

        # termcoloring, converting True/False to Blue/Red colored rows
        colored_tab_data = map(self.__availability_color_mapping, tab_data)

        print(tabulate(tab_headers+colored_tab_data, showindex="always", headers="firstrow"))





def main():
    print colored(__asciiart, 'yellow')
    Digimon = DropRoute()
    Digimon.display_available_regions()


if __name__ == '__main__':
    main()
