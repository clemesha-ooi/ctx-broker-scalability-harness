"""
EC2 provisioning

@file nimbus.py
@author David LaBissoniere
@date 8/17/09
"""

import os
import time
try:
    import json
except ImportError:
    import simplejson as json
from xml.dom.minidom import Document

from twisted.internet import reactor, defer, threads
from twisted.internet.defer import inlineCallbacks,Deferred
from twisted.python import log

import boto

#from cpe.provisioner.util import *
from cpe_provisioner_context import ContextClient, LaunchDescription

class EC2Provisioner(object):

    def __init__(self, configs, accessID=None, secret=None):
        self.configs = configs
        self.accessID = accessID
        self.secret = secret

    @inlineCallbacks
    def start(self, args):
        """Starts new instances on EC2"""
        try:
            type = args['type']
            count = args['count']
        except (KeyError,ValueError):
            raise ProvisionError("start request has invalid args")

        if 'data' in args:
            data = args['data']
        else:
            data = None

        if type not in self.configs:
            raise ProvisionError(type+ " is an unknown instance type")

        config = self.configs[type]
        doc = config.toWorkspaceXml(quantity=count, data=data)

        instances = yield threads.deferToThread(self._launchInstance, doc, config)
        defer.returnValue(instances)

    def _launchInstance(self, doc, config):

        log.msg("attempting to create context with document:\n"+doc)

        contextClient = ContextClient()
        try:
            launches = contextClient.createFromString(doc)

            if len(launches) != 1:
                raise Exception("can only handle one launch at a time right now, sorry")
            launch = launches[0]

            conn = boto.connect_ec2(self.accessID, self.secret)

            res = conn.run_instances(launch.image,
                                     min_count=launch.quantity,
                                     max_count=launch.quantity,
                                     user_data=launch.userdata,
                                     key_name=config.keypair)

            response = []
            for inst in res.instances:
                if not self._waitInstance(inst,"running"):
                    res.stop_all()
                    raise ProvisionError("instance startup timed out")
                response.append({ 'id' : inst.id,
                                  'hostname' : inst.public_dns_name,
                                  'type' : config.name })

            # wait for the context broker to report OK   
            contextClient.monitor()   

            return response

        finally:
            contextClient.cleanup()


    def _waitInstance(self, instance, want_state, timeout=300, step=5):
        cnt = step
        time.sleep(step)
        while instance.update() != want_state:
            if cnt == timeout:
                return False

            time.sleep(step)
            cnt += step

        return True


    @inlineCallbacks
    def stop(self, instances):
        """Terminates the specified list of EC2 instance IDs"""

        if instances is None or len(instances) == 0:
            raise ProvisionError("invalid instance list")

        instances = yield threads.deferToThread(self._stopInstances, instances)

        defer.returnValue(instances)
        

    def _stopInstances(self, instances):
        conn = boto.connect_ec2(self.accessID, self.secret)
        terminating = conn.terminate_instances(instances)
        for inst in terminating:
            self._waitInstance(inst,"terminated",step=1)
        return instances   


class EC2Config(object):
    def __init__(self, name, ami, keypair, data=None):
        self.name = name
        self.ami = ami
        self.keypair = keypair
        self.data = data

    # weak
    def toWorkspaceXml(self, quantity=1, data=None):

        launchData = {}
        if self.data != None:
            for key in self.data:
                launchData[key] = self.data[key]
        if data != None:
            for key in data:
                launchData[key] = data[key]

        # why did I think this was a good idea?

        doc = Document()
        cluster = doc.createElementNS("http://www.globus.org/2008/06/workspace/metadata/logistics", "cluster")

        workspace = doc.createElement("workspace");
        cluster.appendChild(workspace)

        name = doc.createElement("name")
        name.appendChild(doc.createTextNode(self.name))
        workspace.appendChild(name)

        image = doc.createElement("image")
        image.appendChild(doc.createTextNode(self.ami))
        workspace.appendChild(image)

        quantityNode = doc.createElement("quantity")
        quantityNode.appendChild(doc.createTextNode(str(quantity)))
        workspace.appendChild(quantityNode)

        nic = doc.createElement("nic")
        nic.setAttribute("wantlogin","true")
        nic.appendChild(doc.createTextNode("public"))
        workspace.appendChild(nic)

        ctx = doc.createElement("ctx")
        workspace.appendChild(ctx)

        provides = doc.createElement("provides")
        provides.appendChild(doc.createElement("identity"))
        ctx.appendChild(provides)

        role = doc.createElement("role")
        role.setAttribute("hostname","true")
        role.setAttribute("pubkey","true")
        role.appendChild(doc.createTextNode(self.name))
        provides.appendChild(role)

        requires = doc.createElement("requires")
        requires.appendChild(doc.createElement("identity"))
        ctx.appendChild(requires)

        for key in launchData:
            dataNode = doc.createElement("data")
            dataNode.setAttribute("name", key)
            dataNode.appendChild(doc.createCDATASection(launchData[key]))
            requires.appendChild(dataNode)
        
        return cluster.toxml()
