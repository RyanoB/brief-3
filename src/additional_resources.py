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

# 1. Ouverture du port 8080 dans les NSG
execute_command("az network nsg rule create --resource-group " + config["rg_name"] + " "
    + "--nsg-name " + config["vm_name"] + "NSG --name " + config["nsg_name"] + " "
    + " --access Allow --direction Inbound --priority 100 "
    + "--source-address-prefix \"*\" "
    + "--source-port-range \"*\" "
    + "--destination-address-prefix \"*\" "
    + "--destination-port-range 8080")

# 2. Création du disque data (64GB)
execute_command("az disk create --resource-group " + config["rg_name"] + " "
    + "--name " + config["app_disk_name"] + " "
    +  "--sku StandardSSD_LRS --location "
    + config["location"] + " --size-gb 64")

# 3. Lier le disque data avec la VM
execute_command("az vm disk attach -g " + config["rg_name"] + " "
    + "--vm-name " + config["vm_name"] + " "
    + "--name " + config["app_disk_name"]) 

# 4. Creation du FQDN
execute_command("az network public-ip update --resource-group " + config["rg_name"] + " "
    + "--name " + config["appli_nic_name"] + " "
    + "--dns-name " + config["fqdn_name"])

# 5. Blocage des connexions SSH venant de l'exterieur
execute_command("az network nsg rule delete -g " + config["rg_name"] + " --nsg-name " + config["vm_name"] + "NSG -n default-allow-ssh")