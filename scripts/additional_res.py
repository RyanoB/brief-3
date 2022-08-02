import json
import subprocess

open("./logfile_ad","w").close()
open("./errlogfile_ad", "w").close()

log = open("./logfile_ad","a")
errlog = open ("./errlogfile_ad","a")

def execute_command(command, logfile_ad, errlogfile_ad):
    callback = subprocess.run(command, stdout=logfile_ad, stderr=errlogfile_ad, shell=True)

    result = { "output_str": callback.args, "exit_code": callback.returncode }
   
    # Condition de rollback, si une erreur est détectée dans l'exécution des commandes

    return result

with open("./init.json", "r") as file:
    data = json.load(file)

#  1 - CREATION NSG RULE :
execute_command("az network nsg rule create --resource-group " + data["rg_name"] + " "
    + "--nsg-name " + data["vm_name"] + "NSG --name " + data["nsg_name"] + " "
    + " --access Allow --direction Inbound --priority 100 "
    + "--source-address-prefix \"*\" "
    + "--source-port-range \"*\" "
    + "--destination-address-prefix \"*\" "
    + "--destination-port-range 8080", log, errlog)


#  2 - CREATION DATA DISK :
execute_command("az disk create --resource-group " + data["rg_name"] + " "
    + "--name " . data["app_disk_name"] + " "
    +  "--sku StandardSSD_LRS --location "
    + data["location"] + " --size-gb 64", log, errlog)

#  3 - LIER DATA DISK A LA VM :
execute_command("az vm disk attach -g " + data["rg_name"] + " "
    + "--vm-name " + data["vm_name"] + " "
    + "--name " + data["app_disk_name"], log, errlog) 

#  4 - AJOUT FQDN :
execute_command("az network public-ip update --resource-group " + data["rg_name"] + " "
    + "--name " + data["appli_nic_name"] + " "
    + "--dns-name " + data["fqdn_name"], log, errlog)