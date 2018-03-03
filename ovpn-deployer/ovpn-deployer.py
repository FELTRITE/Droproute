import paramiko

class ovpn_deployer():
    
    def __init__(self, ip, username, password):
        self.sshconn = paramiko.SSHClient()
        self.ip = ip
        self.username = username
        self.password = password
        self.__connect__()


    def __connect__(self):
        self.sshconn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        remote_conn_pre.connect(ip,
                                username=username,
                                password=password,
                                look_for_keys=False,
                                allow_agent=False)

    def __del__(self):
    #TODO: Implement ssh conn removel
    pass
        