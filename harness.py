import sys
sys.path.append("nimbus/ctx-agent/ctx/lib/")

import os
import shutil
import logging
from threading import Thread
from actions import DefaultRetrieveAction, InstantiationResult, AmazonInstantiation
from conf import getconfig, getCommonConf, getAmazonConf, DEFAULTCONFIG
from ctx_logging import addFileLogging, configureLogging, getlog
from utils import getlogfilepath, setlogfilepath
from workspace_ctx_retrieve import parsersetup
from cpe_provisioner_context import ContextClient
import nimbus_config_template

class AmazonInstantiationDummy(AmazonInstantiation):

    def __init__(self, commonconf, ec2conf, **kwargs):
        AmazonInstantiation.__init__(self, commonconf, ec2conf)
        self.userdata = kwargs.get("userdata")
        self.count = kwargs.get("count")

    def get_stdout(self, url):
        """
        Uses 'url' as a key mapping to dummy
        values for the test harness
        """
        if url.endswith("user-data"):
            return self.userdata
        return url+str(self.count) #only requirement is these be unique


def config_logging(commonconf, opts, loglevel=logging.DEBUG):
    print "commonconf.logfilepath => ", commonconf.logfilepath
    log = configureLogging(loglevel, trace=opts.trace)
    addFileLogging(log, commonconf.logfilepath, None, loglevel, trace=opts.trace)
    setlogfilepath(commonconf.logfilepath)
    #log.debug("[file logging enabled @ '%s'] " % commonconf.logfilepath)

def get_confs(config_string):
    """
    Returns (commonconf, ec2conf, opts)
    """
    config = getconfig(string=config_string)
    parser = parsersetup()
    (opts, args) = parser.parse_args()
    commonconf = getCommonConf(opts, config)
    ec2conf = getAmazonConf(opts, config)
    return (commonconf, ec2conf, opts)

def create_nimbus_harness_dirs(total, base="/opt/nimbus"):
    if not os.path.exists(base):
        raise IOError("base nimbus dir does not exist at '%s'" % base)
    for i in range(total):
        newdir = base+str(i)
        if not os.path.exists(newdir):
            shutil.copytree(base, newdir)
    return total

def main(run_number, config_string, userdata):
    (commonconf, ec2conf, opts) = get_confs(config_string)
    commonconf.sshdkeypath=os.path.join(os.path.expanduser("~/"), ".ssh/id_rsa.pub") #XXX
    config_logging(commonconf, opts, loglevel=logging.DEBUG)
    ec2_iaction = AmazonInstantiationDummy(commonconf, ec2conf, userdata=userdata, count=run_number)
    ec2_iaction.run()
    iactionresult = ec2_iaction.result
    dra = DefaultRetrieveAction(commonconf, iactionresult)
    dra.run()


if __name__ == "__main__":
    clusterfile = open(sys.argv[1]).read()
    broker_url = sys.argv[2] # e.g: https://tp-x001.ci.uchicago.edu:8443/wsrf/services/NimbusContextBroker 
    broker_id = sys.argv[3] # e.g: /C=ae5d95ac-30aa-4c6b-b92c-84f25c7f3455/CN=localhost
    contextClient = ContextClient(broker_url, broker_id)
    launch_descrips = contextClient.createFromString(clusterfile)

    TOTAL_AGENTS = sum(int(item.quantity) for item in launch_descrips)
    create_nimbus_harness_dirs(TOTAL_AGENTS) #better way?
    print "Starting %s ctx-agents..." % TOTAL_AGENTS
    total = 0
    for ld in launch_descrips:
        cur_quantity = int(ld.quantity)
        print "Current launch description quantity = ", cur_quantity
        while cur_quantity > 0:
            nimbus_dir = "/opt/nimbus"+str(total)
            userdata = ld.userdata
            config_string = nimbus_config_template.render(nimbus_dir)
            thread = Thread(target=main, args=(total, config_string, userdata))
            thread.start()
            total += 1
            cur_quantity -= 1
            print "Started run #%s using dir '%s'" % (total, nimbus_dir)
