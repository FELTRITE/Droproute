from droproute import *
import prompter

__version__ = "1.0"



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
    return False

def interactive_mode(Digimon):
    datacenter_list = Digimon.display_available_regions()
    selected_region_index = prompt_select("Select region", datacenter_list)

    desired_datacenter = datacenter_list[selected_region_index]
    Digimon.deploy_Infrastructure(desired_datacenter)

    Digimon.download_ovpn_key()
    while Digimon.online:
        if not __prompt_route_decommissioning():
            # Proceed only when Decommissioning the route
            break
    Digimon.destroy_Infrastructure()


def main():
    print colored(config.asciiart.format(ver=__version__), 'yellow')
    Digimon = DropRoute()
    interactive_mode(Digimon)


if __name__ == '__main__':
    main()
