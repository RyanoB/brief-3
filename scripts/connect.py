import json
import subprocess as sp

with open("./init.json", "r") as file:
    data = json.load(file)

#fonction de récupération des resource ids 

def get_resource_id(res_name):
    return json.loads(sp.check_output("az resource list --name \"" + res_name + "\"", shell=True).decode())[0]["id"]

# Connection SSH au bastion :

command = str("az network bastion ssh --name \"" + data["bastion_name"] + "\" " 
+ "--resource-group \"" + data["rg_name"] + "\" " 
+ "--target-resource-id " + "\"" + get_resource_id(data["vm_name"]) + "\"" + " " 
+ "--auth-type \"" + data["auth_type"] + "\" " 
+ "--username \"" + data["admin_user_name"] + "\" " 
+ "--ssh-key \"" + data["key_path"] + "\"")

# Redirection de stdout, stdin, stderr

ssh_bastion = sp.Popen(command, stdout=sp.PIPE, stdin=sp.PIPE, stderr=sp.PIPE, shell=True)
print("BWARK ! Test 1")
command_list = b"""
sudo apt update
sudo apt install openjdk-11-jre -y
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins
java -version
"""

# affectation de stdout et stderr via "communicate"
out, err = ssh_bastion.communicate(command_list)

if out is not None:
    out = out.decode()

if err is not None:
    err = err.decode()
print("BWARK ! Test 2")
print(out, err)