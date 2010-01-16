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
        return url+"1"

DEFAULTCONFIG1 = """

# This is the default configuration file for the program.

# It can be changed inline or copied out into a file whose path can
# be passed into the program via command-line (see -h).  If that is done, 
# the program will NOT fall back to this default configuration if there
# is an error or misconfiguration with the supplied config file.


[sshd]

# Absolute path only, the sshd host key
generatedkey: /etc/ssh/ssh_host_rsa_key.pub

# SSHd hosts config is adjusted directly by this program right now, adds
# equiv hostnames and pubkeys for host based authorization across the whole
# contextualization context.

hostbasedconfig: /etc/hosts.equiv
knownhostsconfig: /etc/ssh/ssh_known_hosts


[reginst]

#### Regular instantiation

# Path to metadata server URL file
path: /var/nimbus-metadata-server-url

# Comma separated names of possible identity nics (do NOT use lo, for example).
# These are REAL local interface names that may be present (each is checked for
# an IP configuration).
nicnames: eth0, eth1


[systempaths]

# These can be relative or absolute paths.
hostname: hostname
curl: curl


# ***NOTE: it is unlikely you need to alter the configurations below this line

[taskpaths]

#### Calling order (this is explained in more detail below).
#### 0-etchosts
#### 1-ipandhost
#### 2-thishost
#### 3-data
#### 4-restarts
#### 5-thishostfinalize


#### 0-etchosts
#
# every identity seen is always sent to etchosts
#    arg1: IP
#    arg2: short hostname
#    arg3: FQDN

etchosts: /opt/nimbus1/ctx-scripts/0-etchosts.sh


#### 1-ipandhost
#
# Directory where the scripts live that match the required role names.
# See samples for more explanation.
#
# These role scripts receive:
#    arg1: IP
#    arg2: short hostname
#    arg3: FQDN

ipandhostdir: /opt/nimbus1/ctx-scripts/1-ipandhost


#### 2-thishost
#
# "thishost" scripts are called with network information known about the
# host this program is running on.
#
# Each script receives:
#    arg1: IP
#    arg2: Short local hostname
#    arg3: FQDN
#
# The names of the scripts in this directory must correspond to the interface
# that the context broker knows about, not the local interface which may not
# match.
# 
# Particular scripts may be absent.  The entire directory configuration
# may also be absent.

thishostdir: /opt/nimbus1/ctx-scripts/2-thishost


#### 3-data
#
# The opaque data directory contains scripts that match provided data names.
# If data fields exist in the context, the data is written to a file and
# that file absolute path is sent as only argument to the scripts.
# The scripts are called after 'thishost' but before 'restarts'.

datadir: /opt/nimbus1/ctx-scripts/3-data


#### 4-restarts
#
# The restart directory contains scripts that match provided roles.
#
# After all role information has been added via the ipandhostdir script AND
# after the "thishost" scripts have successfully run, this program will call
# the restart script for each required role it knows about (presumably to
# restart the service now that config has changed).
#
# No arguments are sent.
#
# It is OK for the required role to not have a script in this directory.

restartdir: /opt/nimbus1/ctx-scripts/4-restarts


#### 5-thishostfinalize
#
# The "thishostfinalize" scripts are called with network information known
# about the host this program is running on.  It is called AFTER the restart
# scripts are successfully called.
#
# Each script receives:
#    arg1: IP
#    arg2: Short local hostname
#    arg3: FQDN
#
# The names of the scripts in this directory must correspond to the interface
# that the context broker knows about, not the local interface which may not
# match.
# 
# Particular scripts may be absent.  The entire directory configuration
# may also be absent.

thishostfinalizedir: /opt/nimbus1/ctx-scripts/5-thishost-finalize


# "problem" script
# In case of problems, could call poweroff.  This script will be called after
# an attempt to notify the service of the error (that notification provides
# a log of the run to the context broker).
#
# Must be configured if "--poweroff" (-p) argument is used, will not be
# consulted if that argument is not used.

problemscript: /opt/nimbus1/ctx-scripts/problem.sh


[ctxservice]

# logfile of the run
# If config is missing, no log will be written and nothing will be sent to
# service for error reporting.
logfilepath: /opt/nimbus1/ctxlog.txt

# Directory where the program can write temporary files
scratchspacedir: /opt/nimbus1/ctx/tmp

retr_template: /opt/nimbus1/ctx/lib/retr-template-001.xml
retr_template2: /opt/nimbus1/ctx/lib/retr-template-002.xml
err_template: /opt/nimbus1/ctx/lib/err-template-001.xml
err_template2: /opt/nimbus1/ctx/lib/err-template-002.xml
ok_template: /opt/nimbus1/ctx/lib/ok-template-001.xml
ok_template2: /opt/nimbus1/ctx/lib/ok-template-002.xml



[ec2]

#### EC2 instantiation (alternative to regular method)

# URLs for the Amazon REST instance data API
localhostnameURL:  http://169.254.169.254/2007-01-19/meta-data/local-hostname
publichostnameURL: http://169.254.169.254/2007-01-19/meta-data/public-hostname
localipURL:        http://169.254.169.254/2007-01-19/meta-data/local-ipv4
publicipURL:       http://169.254.169.254/2007-01-19/meta-data/public-ipv4
publickeysURL:     http://169.254.169.254/2007-01-19/meta-data/public-keys/
userdataURL:       http://169.254.169.254/2007-01-19/user-data


"""



if __name__ == "__main__":
    config = getconfig(string=DEFAULTCONFIG1)
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
    USERDATA=UDPATH+"/userdata-1"

    ec2_iaction = AmazonInstantiationDummy(commonconf, ec2conf, userdata=USERDATA)
    ec2_iaction.run()
    iactionresult = ec2_iaction.result
    print iactionresult.ctx_keytext, iactionresult.ctx_certtext

    dra = DefaultRetrieveAction(commonconf, iactionresult)
    dra.run()

