# Credit goes to angristan
# https://github.com/angristan/openvpn-install

# Set custom Variables
export AUTO_INSTALL=y
export CONTINUE=y
export DNS=9 #Google DNS
export CLIENT='{ovpn_client_filename}'


# Download & install
curl -O https://raw.githubusercontent.com/angristan/openvpn-install/master/openvpn-install.sh
chmod +x openvpn-install.sh
./openvpn-install.sh
rm ./openvpn-install.sh


# Serve .ovpn keyfile for single download on server
#TODO: Figure out how to SSL this shit
cd /root
apt -y update
apt -y install woof
woof -p '{random_server_port}' -c 1 ./$CLIENT.ovpn
rm ./$CLIENT.ovpn