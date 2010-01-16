import sys
sys.path.append("nimbus/ctx-agent/ctx/lib/")
import logging
from actions import DefaultRetrieveAction, InstantiationResult, AmazonInstantiation
from conf import getconfig, getCommonConf, getAmazonConf, DEFAULTCONFIG
from ctx_logging import addFileLogging, configureLogging, getlog
from utils import getlogfilepath, setlogfilepath
from workspace_ctx_retrieve import parsersetup

class AmazonInstantiationDummy(AmazonInstantiation):

    def __init__(self, commonconf, ec2conf, **kwargs):
        AmazonInstantiation.__init__(self, commonconf, ec2conf)
        self.userdata = kwargs.get("userdata")

    def get_stdout(self, url):
        """
        Uses 'url' as a key mapping to dummy
        values for the test harness
        """
        print "get_stdout url => ", url
        if url.endswith("user-data"):
            udata = open(self.userdata).read()
            return udata
        return url+"0"


if __name__ == "__main__":
    config = getconfig(string=DEFAULTCONFIG)
    parser = parsersetup()
    (opts, args) = parser.parse_args()

    commonconf = getCommonConf(opts, config)
    commonconf.sshdkeypath="/Users/alexclemesha/.ssh/id_rsa.pub"
    print "commonconf.logfilepath => ", commonconf.logfilepath
    loglevel = logging.DEBUG
    log = configureLogging(loglevel, trace=opts.trace)
    addFileLogging(log, commonconf.logfilepath, None, loglevel, trace=opts.trace)
    setlogfilepath(commonconf.logfilepath)
    #log.debug("[file logging enabled @ '%s'] " % commonconf.logfilepath)

    ec2conf = getAmazonConf(opts, config)
    print "userdataURL => ", ec2conf.userdataURL
    UDPATH="/var/folders/eK/eKugYWFkE7uHqQgecWLdHE+++TI/-Tmp-/tmpWal9zX"
    USERDATA=UDPATH+"/userdata-0"

    ec2_iaction = AmazonInstantiationDummy(commonconf, ec2conf, userdata=USERDATA)
    ec2_iaction.run()
    iactionresult = ec2_iaction.result
    print iactionresult.ctx_keytext, iactionresult.ctx_certtext

    dra = DefaultRetrieveAction(commonconf, iactionresult)
    dra.run()

