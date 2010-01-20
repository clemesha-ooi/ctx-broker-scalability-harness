export NIMBUS_CLOUD_CLIENT="/Users/alexclemesha/ctx-broker-scalability-harness/nimbus-cloud-client-014/"
#python run.py https://tp-x005.ci.uchicago.edu:8443/wsrf/services/NimbusContextBroker /C=ae5d95ac-30aa-4c6b-b92c-84f25c7f3455/CN=localhost

python harness.py harness.xml https://tp-vm1.ci.uchicago.edu:8445/wsrf/services/NimbusContextBroker /O=Grid/OU=GlobusTest/OU=simple-workspace-ca/CN=host/tp-vm1.ci.uchicago.edu
