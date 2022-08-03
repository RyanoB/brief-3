import json
import subprocess
import sys

import infrastructure
import jenkins_installer

if sys.argv[1] == "--infrastrucure-only":
    infrastructure.run()
elif sys.argv[1] == "--service-only":
    jenkins_installer.run()
else:
    infrastructure.run()
    jenkins_installer.run()