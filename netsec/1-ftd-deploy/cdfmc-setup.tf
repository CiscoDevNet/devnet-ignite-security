# Access Policy

# Data Sources
data "fmc_port" "http" {
    name = "HTTP"
}
data "fmc_port" "https" {
    name = "HTTPS"
}
data "fmc_port" "ssh" {
    name = "SSH"
}
data "fmc_intrusion_policy" "ips_policy" {
    name = "Security Over Connectivity"
}

# Network Objects
resource "fmc_network" "app_subnet" {
  name        = "${local.env_name}-app_subnet"
  prefix      = aws_subnet.app_subnet.cidr_block
  description = "App Network"
}

# Host Objects
resource "fmc_host" "app_server" {
    name        = "${local.env_name}-app_server"
    ip          = aws_instance.app.private_ip
    description = "App Server"
}

# IPS Policy
resource "fmc_intrusion_policy" "ips_policy" {
    name            = "${local.env_name}-ips_policy"
    inspection_mode = "DETECTION"
    base_policy_id   = data.fmc_intrusion_policy.ips_policy.id
}

# Access Control Policy
resource "fmc_access_control_policy" "access_policy" {
  name           = "${local.env_name}-Access-Policy"
  default_action = "BLOCK"
  rules = [
    {
      section            = "mandatory"
      action             = "ALLOW"
      name               = "${local.env_name}_permit_outbound"
      enabled            = true
      send_events_to_fmc = true
      log_files          = false
      log_begin          = true
      log_end            = true
      source_network_objects = [
        {
          id = fmc_network.app_subnet.id
          type =  "Network"
        }
      ]
      destination_port_objects = [
        {
          id = data.fmc_port.http.id
        }
      ]
      intrusion_policy_id = fmc_intrusion_policy.ips_policy.id
    },  
    {
      section            = "mandatory"
      action             = "ALLOW"
      name               = "${local.env_name}_access_to_app_server"
      enabled            = true
      send_events_to_fmc = true
      log_files          = false
      log_begin          = true
      log_end            = true
      destination_network_objects = [
        {
          id = fmc_host.app_server.id
          type =  "Host"
        }
      ]
      destination_port_objects = [
        {
          id = data.fmc_port.ssh.id
        }
      ]
      intrusion_policy_id = fmc_intrusion_policy.ips_policy.id
    }
  ]
}



# FTD registration
# we need to make sure the FTDv has finished provisioning before registration — this can be resolved by a custom AMI (container)
resource "null_resource" "wait_for_ftdv_to_finish_booting" {
  # If an IP changes, these scripts will run again
  triggers = {
    nodes_ips = var.ftdv_mgmt_private_ip == "" ? aws_network_interface.ftd_management.private_ip : var.ftdv_mgmt_private_ip
  }

  provisioner "local-exec" {
    command = "/bin/bash wait_for_ftdv.sh ${aws_eip.ftd-mgmt-EIP.public_dns}"

  }

  depends_on = [aws_instance.ftdv]
}

# Register FTD to FMC
resource "sccfm_ftd_device" "ftd1" {
  name = "${local.env_name}-FTDv"
  licenses = [
    "BASE",
    "MALWARE",
    "URLFilter",
    "THREAT"
  ]
  virtual = true
  access_policy_name = fmc_access_control_policy.access_policy.name
  #performance_tier = var.ftd_performance_tier
  performance_tier = "FTDv5"
}

output "debug_ftdv_performance_tier" {
  value = var.ftdv_performance_tier
}


resource "sccfm_ftd_device_onboarding" "ftd1" {
  ftd_uid = sccfm_ftd_device.ftd1.id
  depends_on = [null_resource.wait_for_ftdv_to_finish_booting]
}
