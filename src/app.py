import json
import subprocess
import sys

import infrastructure
import jenkins_installer

if len(sys.argv) >= 2:
    if sys.argv[1] == "--deploy":
        infrastructure.run()
    elif sys.argv[1] == "--install":
        jenkins_installer.run()
    else:
        print("Erreur : Argument inconnu !")
else:
    infrastructure.run()
    jenkins_installer.run()