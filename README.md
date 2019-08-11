# Droproute

<img src="https://raw.githubusercontent.com/feltrite/Droproute/logo-view-branch/droproute.jpg" width="300" align="right">
Automated VPN deployment 

short for Droplet-Route,
Droproute is a script that deployes a minimal Digital Ocean
droplet with a configured OpenVPN server. the user specifies the desired
droplet region (country/datacenter).

outputs an ovpn client config.


### Installation
Run the following command in the script directory to install package requirements.
```
git clone https://github.com/feltrite/Droproute.git
cd Droproute/
pip install -r Requirements.txt
```

### Usage 
After installing dependencies, have fun
```
python main.py
```
