import sys
sys.path.append("nimbus/ctx-agent/ctx/lib/")

from actions import DefaultRetrieveAction, InstantiationResult, AmazonInstantiation
from conf import getconfig, getCommonConf, getAmazonConf, DEFAULTCONFIG
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
        return url


if __name__ == "__main__":
    config = getconfig(string=DEFAULTCONFIG)
    parser = parsersetup()
    (opts, args) = parser.parse_args()

    commonconf = getCommonConf(opts, config)
    commonconf.sshdkeypath="/Users/alexclemesha/.ssh/id_rsa.pub"

    ec2conf = getAmazonConf(opts, config)
    print "userdataURL => ", ec2conf.userdataURL
    USERDATA="/var/folders/eK/eKugYWFkE7uHqQgecWLdHE+++TI/-Tmp-/tmp4nMr4o/userdata-0"

    ec2_iaction = AmazonInstantiationDummy(commonconf, ec2conf, userdata=USERDATA)
    ec2_iaction.run()
    iactionresult = ec2_iaction.result
    print iactionresult.ctx_keytext, iactionresult.ctx_certtext

    dra = DefaultRetrieveAction(commonconf, iactionresult)
    dra.run()

