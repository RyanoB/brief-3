
import json
import subprocess

open("./ouput.log","w").close()
open("./error.log", "w").close()

output_log_file = open("./ouput.log","a")
error_log_file = open ("./error.log","a")

def execute_command(command):
    callback = subprocess.run(command, shell=True)

    result = { "output_str": callback.args, "exit_code": callback.returncode }

    return result

def get_resource_id(res_name, res_group):
    return json.loads(subprocess.check_output("az resource list --name \"" + res_name + "\" --resource-group " + res_group, shell=True).decode())[0]["id"]

with open("./config.json", "r") as file:
    config = json.load(file)

# Connection SSH au bastion :

# az network bastion ssh --name JenkinsBastion --resource-group JenkinsTest02 --target-resource-id "/subscriptions/a1f74e2d-ec58-4f9a-a112-088e3469febb/resourceGroups/JenkinsTest02/providers/Microsoft.Compute/virtualMachines/VMApp" --auth-type ssh-key --username noa --ssh-key "/home/noa/.ssh/id_rsa"
command = str("az network bastion ssh --name \"" + config["bastion_name"] + "\" " 
+ "--resource-group \"" + config["rg_name"] + "\" " 
+ "--target-resource-id " + "\"" + get_resource_id(config["vm_name"], config["rg_name"]) + "\"" + " " 
+ "--auth-type ssh-key " 
+ "--username \"" + config["admin_user_name"] + "\" " 
+ "--ssh-key \"" + config["key_path"] + "\"")

command_list = b"""
sudo apt update
sudo apt install openjdk-11-jre -y
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt-get update
sudo apt-get install jenkins
"""

# Redirection de stdout, stdin, stderr

bastion_shell = subprocess.Popen(command, stdin=subprocess.PIPE, shell=True)

print("BWARK ! Test 1")

bastion_shell.communicate(command_list)

print("BWARK ! Test 2")