
from cpe_provisioner_ec2 import EC2Config


if __name__ == "__main__":
    print EC2Config('foo', 'abc123', 'xxx').toWorkspaceXml()
