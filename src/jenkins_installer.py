import json
import subprocess
from datetime import datetime

log_file = open("./logs/jenkins_installer.log","a")

def get_resource_id(res_name, res_group):
    return json.loads(subprocess.check_output("az resource list --name \"" + res_name + "\" --resource-group " + res_group, shell=True).decode())[0]["id"]

with open("./config.json", "r") as file:
    config = json.load(file)

def run():
    log_file.write("\n=== SCRIPT 'jenkins_installer.py' ENDED AT " + str(datetime.now()) + " ===\n")
    # 1. Connexion SSH vers le Bastion
    bastion_shell = subprocess.Popen("az network bastion ssh --name \"" + config["bastion_name"] + "\" " 
    + "--resource-group \"" + config["rg_name"] + "\" " 
    + "--target-resource-id " + "\"" + get_resource_id(config["vm_name"], config["rg_name"]) + "\"" + " " 
    + "--auth-type ssh-key " 
    + "--username \"" + config["admin_user_name"] + "\" " 
    + "--ssh-key \"" + config["key_path"] + "\"", stdout=log_file, stderr=log_file, stdin=subprocess.PIPE, shell=True)

    # 2. Envoi des commandes d'installation de Jenkins
    bastion_shell.communicate(b"""
        sudo apt update
        sudo apt install openjdk-11-jre -y
        curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
        echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
        sudo apt-get update
        sudo apt-get install jenkins
        sudo cat /var/lib/jenkins/secrets/initialAdminPassword
    """)


def rollback():
    # 1. Connexion SSH vers le Bastion
    bastion_shell = subprocess.Popen("az network bastion ssh --name \"" + config["bastion_name"] + "\" " 
    + "--resource-group \"" + config["rg_name"] + "\" " 
    + "--target-resource-id " + "\"" + get_resource_id(config["vm_name"], config["rg_name"]) + "\"" + " " 
    + "--auth-type ssh-key " 
    + "--username \"" + config["admin_user_name"] + "\" " 
    + "--ssh-key \"" + config["key_path"] + "\"", stdin=subprocess.PIPE, shell=True)

    # 2. Envoi des commandes d'installation de Jenkins
    bastion_shell.communicate(b"""
        sudo apt update
        sudo apt remove jenkins
        sudo apt remove openjdk-11-jre -y
    """)