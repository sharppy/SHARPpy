import os
import glob
import time
from datetime import datetime

path = os.environ.get('Build_ArtifactStagingDirectory'.upper())
print(path)
timeout = 60*5
now = datetime.now()
files = glob.glob(path + '/*zip')
while len(files) != 2 and (datetime.now() - now).total_seconds() < timeout: 
    files = glob.glob(path + '/*zip')
    print(files)   

print("ALL FILES IN THE BUILD ARTIFACT STAGING DIRECTORY...NEXT STEP SHOULD BE DEPLOYING") 
