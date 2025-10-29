resource "aws_cloudformation_stack" "autoscale_cf_stack" {
  count = 1
  name          = "${local.env_name}-cf"
  template_body = file("./autoscale/deploy_ngfw_autoscale.yaml")
  capabilities = ["CAPABILITY_AUTO_EXPAND", "CAPABILITY_NAMED_IAM"]

  parameters = {
    VpcId: aws_vpc.service_vpc.id
    PodNumber: var.env_pod_number
    NoOfAZs: 1
    ListOfAZs: var.aws_az
    MgmtInterfaceSG: aws_security_group.allow_egress_ingress_ssh.id
    MgmtSubnetId: aws_subnet.mgmt_subnet.id
    InsideSubnetId: aws_subnet.inside_subnet.id
    InsideInterfaceSG: aws_security_group.allow_all.id
    OutsideSubnetId: aws_subnet.outside_subnet.id
    OutsideInterfaceSG: aws_security_group.allow_all.id
    LambdaSubnets: aws_subnet.lambda_subnet[0].id
    LambdaSG: aws_security_group.allow_all.id
    loadBalancerARN: aws_lb.gwlb.arn
    AmiID: data.aws_ami.ftdv.id
    KeyPairName: aws_key_pair.public_key.key_name
    fmcServer: "api.us.security.cisco.com"
    fmcOperationsApiToken: var.sccfm_api_token
    fmcDeviceGrpName: local.ftd_device_group
    fmcPerformanceLicenseTier: "FTDv30"
    fmcMetricsUsername: ""
    fmcMetricsPassword: ""
    ngfwPassword: random_password.ftd_pass.result
    S3BktName: "devnetlambda"
  }

}

