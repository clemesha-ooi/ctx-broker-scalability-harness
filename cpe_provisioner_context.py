"""
Nimbus context broker client wrapper

@file context.py
@author David LaBissoniere
@date 8/18/09
"""

import os
from subprocess import Popen, PIPE, STDOUT
from shutil import rmtree
import tempfile


class ContextClient(object):
    """Interfaces with Nimbus cloud client to provide contextualization methods"""


    def __init__(self, brokerUrl, brokerId):
        self._tempClusterPath = None
        self._tempDirPath = None
        self.brokerUrl = brokerUrl
        self.brokerId = brokerId

    def createFromString(self, cluster):
        """
        Creates a new context and generates userdata
        Returns a list of LaunchDescription objects
        @param cluster the XML cluster description
        """
        fd,self._tempClusterPath = tempfile.mkstemp(text=True)
        f = os.fdopen(fd,"w")
        f.write(cluster)
        f.close()

        return self.createFromFile(self._tempClusterPath)

    def createFromFile(self, clusterPath):
        """
        Creates a new context and generates userdata
        Returns a list of LaunchDescription objects
        @param clusterPath path to the XML cluster description
        """
        if not os.path.isfile(clusterPath):
            raise Exception(clusterPath+" does not exist")

        self._tempDirPath = tempfile.mkdtemp()

        args = [_CLOUD_CLIENT_BIN, '--init-context', self._tempDirPath,
                '--cluster', clusterPath, '--broker-url', self.brokerUrl,
                '--broker-id', self.brokerId]

        proc = Popen(args, stdout=PIPE, stderr=STDOUT)
        (out,err) = proc.communicate()
        if proc.wait() != 0:
            raise ContextClientError("Creating context failed. Output: "+out)

        manifest = open(os.path.join(self._tempDirPath,"manifest.txt"))
        lines = manifest.readlines()
        manifest.close()

        lds = []
        for line in lines:
            image,quantity,path = line.split()

            userdataFile = open(path)
            userdata = userdataFile.read()
            userdataFile.close()

            lds.append(LaunchDescription(image,quantity,userdata))

        return lds

    def monitor(self, epr=None, poll_ms=1000):
        """Watches for the contextualization to be successfully completed """

        if epr is None:
            epr = os.path.join(self._tempDirPath, 'context-epr.xml')
        args = ['sh', _WORKSPACE_BIN, '--ctx-monitor',
                '--eprFile', epr,
                '--poll-delay', str(poll_ms)]

        proc = Popen(args, stdout=PIPE, stderr=STDOUT)
        (out,err) = proc.communicate()
        if proc.wait() != 0:
            raise ContextClientError("Monitoring context failed. Output: "+out)
        

    def cleanup(self):
        """Cleans up temporary files"""
        try:
            if self._tempClusterPath != None:
                os.remove(self._tempClusterPath)
            if self._tempDirPath != None:
                rmtree(self._tempDirPath)
        except:
            #cleanup is best effort only
            pass


class LaunchDescription(object):
    """Parameters for VM launch"""
    def __init__(self, image, quantity, userdata):
        self.image = image
        self.quantity = quantity
        self.userdata = userdata

class ContextClientError(Exception):
    pass



_CLOUD_CLIENT_DIR = "/opt/nimbus-cloud-client-014/"
if (os.getenv("NIMBUS_CLOUD_CLIENT")):
    _CLOUD_CLIENT_DIR = os.getenv("NIMBUS_CLOUD_CLIENT")

_CLOUD_CLIENT_BIN = os.path.join(_CLOUD_CLIENT_DIR, "bin/cloud-client.sh")
_WORKSPACE_BIN = os.path.join(_CLOUD_CLIENT_DIR, "lib/workspace.sh")

if not os.path.isfile(_CLOUD_CLIENT_BIN):
    raise ContextClientError(_CLOUD_CLIENT_BIN+" does not exist")

if not os.path.isfile(_WORKSPACE_BIN):
    raise ContextClientError(_WORKSPACE_BIN+" does not exist")
    
