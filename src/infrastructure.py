import json
import subprocess

def execute_command(command):
    callback = subprocess.run(command, shell=True)

    result = { "output_str": callback.args, "exit_code": callback.returncode }

    return result

def get_resource_id(res_name, res_group):
    return json.loads(subprocess.check_output("az resource list --name \"" + res_name + "\" --resource-group " + res_group, shell=True).decode())[0]["id"]

with open("./config.json", "r") as file:
    config = json.load(file)

def run():
    # 1. Création ResourceGroup
    execute_command("az group create --name " + config["rg_name"] + " --location " + config["location"])

    # 2. Création VNET
    execute_command("az network vnet create --name " + config["vnet_name"] + " "
            + "--resource-group " + config["rg_name"] + " "
            + "--address-prefix " + config["vnet_prefix"])

    # 3. Création IP publique Bastion
    execute_command("az network public-ip create --resource-group " + config["rg_name"] + " "
            + "--name " + config["bastion_nic_name"] + " "
            + "--sku " + config["sku"] + " "
            + "--location " + config["location"])

    # 4. Création du AzureBastionSubnet
    execute_command("az network vnet subnet create --name AzureBastionSubnet "
            + "--resource-group " + config["rg_name"] + " "
            + "--vnet-name " + config["vnet_name"] + " "
            + "--address-prefixes " + config["bastion_subnet_prefix"])

    # 5. Création du subnet principal
    execute_command("az network vnet subnet create --name " + config["appli_subnet_name"] + " "
            + "--resource-group " + config["rg_name"] + " "
            + "--vnet-name " + config["vnet_name"] + " "
            + "--address-prefixes " + config["appli_subnet_prefix"]) 

    # 6. Création IP publique de Jenkins
    execute_command("az network public-ip create --resource-group " + config["rg_name"] + " --name " + config["appli_nic_name"])

    # 7. Création VM Appli
    execute_command("az vm create --name " + config["vm_name"] + " "
        + "--resource-group " + config["rg_name"] + " "
        + "--image Debian:debian-10:10:latest "
        + "--public-ip-address " + config["appli_nic_name"] + " "
        + "--subnet " + config["appli_subnet_name"] + " --vnet-name " + config["vnet_name"] + " "
        + "--nic-delete-option delete "
        + "--os-disk-delete-option delete "
        + "--data-disk-delete-option delete "
        + "--ssh-key-values ~/.ssh/id_rsa.pub "
        + "--admin-username " + config["admin_user_name"] + " "
        + "--authentication-type ssh")
            
    # 8. Création Bastion
    execute_command("az network bastion create --name " + config["bastion_name"] + " "
        + "--public-ip-address " + config["bastion_nic_name"] + " "
        + "--resource-group " + config["rg_name"] + " "
        + "--vnet-name " + config["vnet_name"] + " "
        + "--location " + config["location"])

    # 9. Ouverture du tunnel
    execute_command("az resource update --include-response-body --ids \"" + get_resource_id(config["bastion_name"], config["rg_name"]) + "\" --set properties.enableTunneling=True")
    
    # 10. Ouverture du port 8080 dans les NSG
    execute_command("az network nsg rule create --resource-group " + config["rg_name"] + " "
        + "--nsg-name " + config["vm_name"] + "NSG --name " + config["nsg_name"] + " "
        + " --access Allow --direction Inbound --priority 100 "
        + "--source-address-prefix \"*\" "
        + "--source-port-range \"*\" "
        + "--destination-address-prefix \"*\" "
        + "--destination-port-range 8080")

    # 11. Création du disque data (64GB)
    execute_command("az disk create --resource-group " + config["rg_name"] + " "
        + "--name " + config["app_disk_name"] + " "
        +  "--sku StandardSSD_LRS --location "
        + config["location"] + " --size-gb 64")

    # 12. Lier le disque data avec la VM
    execute_command("az vm disk attach -g " + config["rg_name"] + " "
        + "--vm-name " + config["vm_name"] + " "
        + "--name " + config["app_disk_name"]) 

    # 13. Creation du FQDN
    execute_command("az network public-ip update --resource-group " + config["rg_name"] + " "
        + "--name " + config["appli_nic_name"] + " "
        + "--dns-name " + config["fqdn_name"])

    # 14. Blocage des connexions SSH venant de l'exterieur
    execute_command("az network nsg rule delete -g " + config["rg_name"] + " --nsg-name " + config["vm_name"] + "NSG -n default-allow-ssh")