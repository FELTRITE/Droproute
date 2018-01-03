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



    def list_available_regions(self):
        response = self.api('get', 'regions')
        regions = response['regions']
        tab_data = [[iter['available'], iter['name'], iter['slug']] for iter in regions]
        print(tabulate(tab_data, showindex="always"))





def main():
    print colored(__asciiart, 'yellow')
    Digimon = DropRoute()


if __name__ == '__main__':
    main()
