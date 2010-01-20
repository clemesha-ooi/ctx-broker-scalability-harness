from string import Template 

CONFIG_TEMPLATE = """

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

etchosts: $nimbus_dir/ctx-scripts/0-etchosts.sh


#### 1-ipandhost
#
# Directory where the scripts live that match the required role names.
# See samples for more explanation.
#
# These role scripts receive:
#    arg1: IP
#    arg2: short hostname
#    arg3: FQDN

ipandhostdir: $nimbus_dir/ctx-scripts/1-ipandhost


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

thishostdir: $nimbus_dir/ctx-scripts/2-thishost


#### 3-data
#
# The opaque data directory contains scripts that match provided data names.
# If data fields exist in the context, the data is written to a file and
# that file absolute path is sent as only argument to the scripts.
# The scripts are called after 'thishost' but before 'restarts'.

datadir: $nimbus_dir/ctx-scripts/3-data


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

restartdir: $nimbus_dir/ctx-scripts/4-restarts


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

thishostfinalizedir: $nimbus_dir/ctx-scripts/5-thishost-finalize


# "problem" script
# In case of problems, could call poweroff.  This script will be called after
# an attempt to notify the service of the error (that notification provides
# a log of the run to the context broker).
#
# Must be configured if "--poweroff" (-p) argument is used, will not be
# consulted if that argument is not used.

problemscript: $nimbus_dir/ctx-scripts/problem.sh


[ctxservice]

# logfile of the run
# If config is missing, no log will be written and nothing will be sent to
# service for error reporting.
logfilepath: $nimbus_dir/ctxlog.txt

# Directory where the program can write temporary files
scratchspacedir: $nimbus_dir/ctx/tmp

retr_template: $nimbus_dir/ctx/lib/retr-template-001.xml
retr_template2: $nimbus_dir/ctx/lib/retr-template-002.xml
err_template: $nimbus_dir/ctx/lib/err-template-001.xml
err_template2: $nimbus_dir/ctx/lib/err-template-002.xml
ok_template: $nimbus_dir/ctx/lib/ok-template-001.xml
ok_template2: $nimbus_dir/ctx/lib/ok-template-002.xml



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

def render(nimbus_dir):
    tmpl = Template(CONFIG_TEMPLATE)
    return tmpl.substitute({"nimbus_dir":nimbus_dir})

if __name__ == "__main__":
    print render("/opt/nimbus")
