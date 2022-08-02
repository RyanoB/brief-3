import json
import subprocess

exit_code_total = 0

open("./logfile","w").close()
open("./errlogfile", "w").close()

log = open("./logfile","a")
errlog = open ("./errlogfile","a")

def execute_command(command, logfile, errlogfile):
    callback = subprocess.run(command, stdout=logfile, stderr=errlogfile, shell=True)

    result = { "output_str": callback.args, "exit_code": callback.returncode }
   
    # Condition de rollback, si une erreur est détectée dans l'exécution des commandes

    if (result["exit_code"]) != 0:
        exit_code_total = exit_code_total+1
    else:
        exit_code_total = 0

    return result

with open("./init.json", "r") as file:
    data = json.load(file)

# 0. Suppression d'un groupe de ressource déjà éxistantes

# execute_command("az group delete --resource-group " + data["rg_name"] + " --yes", log)

# 1. Création du resource group

execute_command("az group create --name " + data["rg_name"] + " --location " + data["location"], log, errlog)

# 2. Création du VNET

execute_command("az network vnet create --name " + data["vnet_name"] + " "
        + "--resource-group " + data["rg_name"] + " "
        + "--address-prefix " + data["vnet_prefix"], log, errlog)

# 3. Création IP publique Bastion

execute_command("az network public-ip create --resource-group " + data["rg_name"] + " "
        + "--name " + data["bastion_nic_name"] + " "
        + "--sku " + data["sku"] + " "
        + "--location " + data["location"], log, errlog)

# 4. Création du subnet Bastion

execute_command("az network vnet subnet create --name AzureBastionSubnet "
        + "--resource-group " + data["rg_name"] + " "
        + "--vnet-name " + data["vnet_name"] + " "
        + "--address-prefixes " + data["bastion_subnet_prefix"], log, errlog)

# 5. Création du subnet Appli

execute_command("az network vnet subnet create --name " + data["appli_subnet_name"] + " "
        + "--resource-group " + data["rg_name"] + " "
        + "--vnet-name " + data["vnet_name"] + " "
        + "--address-prefixes " + data["appli_subnet_prefix"], log, errlog) 

# 6. Public IP VM Appli

execute_command("az network public-ip create --resource-group " + data["rg_name"] + " --name " + data["appli_nic_name"], log, errlog)

# 7. Création VM Appli

execute_command("az vm create --name " + data["vm_name"] + " "
    + "--resource-group " + data["rg_name"] + " "
    + "--image Debian:debian-10:10:latest "
    + "--public-ip-address " + data["appli_nic_name"] + " "
    + "--subnet " + data["appli_subnet_name"] + " --vnet-name " + data["vnet_name"] + " "
    + "--nic-delete-option delete "
    + "--os-disk-delete-option delete "
    + "--data-disk-delete-option delete "
    + "--generate-ssh-keys "
    + "--admin-username " + data["admin_user_name"] + " "
    + "--authentication-type ssh", log, errlog)
        
# # 8. Création Bastion

execute_command("az network bastion create --name " + data["bastion_name"] + " "
    + "--public-ip-address " + data["bastion_nic_name"] + " "
    + "--resource-group " + data["rg_name"] + " "
    + "--vnet-name " + data["vnet_name"] + " "
    + "--location " + data["location"], log, errlog)

# 9. Connection SSH entre Bastion et VM

# Fonction de récupération des resource ids 
def get_resource_id(res_name):
    return json.loads(subprocess.check_output("az resource list --name \"" + res_name + "\"", shell=True).decode())[0]["id"]

# Commande pour ouvrir le tunnel

execute_command("az resource update --include-response-body --ids \"" + get_resource_id(data["bastion_name"]) + "\" --set properties.enableTunneling=True", log, errlog)

# az network bastion tunnel --name "<BastionName>" --resource-group "<ResourceGroupName>" --target-resource-id "<VMResourceId or VMSSInstanceResourceId>" --resource-port "<TargetVMPort>" --port "<LocalMachinePort>"

print("Total exit codes :", exit_code_total)
print("\"" + get_resource_id(data["bastion_name"]) + "\"")