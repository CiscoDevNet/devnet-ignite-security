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
        },
        {
          id = data.fmc_port.https.id
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
  performance_tier = "FTDv30"
}

resource "sccfm_ftd_device_onboarding" "ftd1" {
  ftd_uid = sccfm_ftd_device.ftd1.id
  depends_on = [null_resource.wait_for_ftdv_to_finish_booting]
}

# Configure FTD interfaces and routes in FMC
data "fmc_device" "ftd1" {
    depends_on = [sccfm_ftd_device_onboarding.ftd1]
    name = "${local.env_name}-FTDv"
}

resource "fmc_security_zone" "outside_sz" {
  name           = "${local.env_name}-Outside-sz"
  interface_type = "ROUTED"
}

resource "fmc_security_zone" "inside_sz" {
  name           = "${local.env_name}-Inside-sz"
  interface_type = "ROUTED"
}

resource "fmc_device_physical_interface" "outside_int" {
    depends_on = [fmc_security_zone.outside_sz]
    name = "TenGigabitEthernet0/1"
    logical_name = "${local.env_name}-Outside"
    device_id = data.fmc_device.ftd1.id
    security_zone_id = fmc_security_zone.outside_sz.id
    mtu = 1806
    mode = "NONE"
    ipv4_dhcp_obtain_route = true
    ipv4_dhcp_route_metric = 1
    enabled = true
}

resource "fmc_device_physical_interface" "inside_int" {
    depends_on = [fmc_security_zone.inside_sz]
    name = "TenGigabitEthernet0/0"
    logical_name = "${local.env_name}-Inside"
    device_id = data.fmc_device.ftd1.id
    security_zone_id = fmc_security_zone.inside_sz.id
    mtu = 1806
    mode = "NONE"
    ipv4_dhcp_obtain_route = true
    ipv4_dhcp_route_metric = 1
    enabled = true
}

resource "fmc_device_vtep_policy" "vtep" {
    device_id = data.fmc_device.ftd1.id
    vteps = [
      {
        source_interface_id      = fmc_device_physical_interface.inside_int.id
        nve_number               = 1
        neighbor_discovery       = "NONE"
        encapsulation_type       = "GENEVE"
      }
    ]
}

resource "fmc_device_vni_interface" "vni_int" {
    device_id               = data.fmc_device.ftd1.id
    vni_id                  = 1
    nve_number              = fmc_device_vtep_policy.vtep.vteps[0].nve_number
    logical_name            = "vni1"
    enable_proxy            = true
    security_zone_id        = fmc_security_zone.inside_sz.id
}

resource "fmc_device_ipv4_static_route" "inside_static_route" {
    device_id               = data.fmc_device.ftd1.id
    interface_logical_name  = "${local.env_name}-Inside"
    interface_id            = fmc_device_physical_interface.inside_int.id
    destination_networks = [
      {
        id = "cb7116e8-66a6-480b-8f9b-295191a0940a" # any ipv4
      }
    ]
    metric_value         = 1
    gateway_host_literal = aws_network_interface.ftd_inside.private_ip
}

# Configure platform policy

resource "fmc_ftd_platform_settings" "platform_settings" {
    name        = "${local.env_name}-platform-settings"
    description = "${local.env_name} platform settings"
}

resource "fmc_policy_assignment" "platform_policy_assignment" {
    policy_id               = fmc_ftd_platform_settings.platform_settings.id
    policy_type             = "FTDPlatformSettingsPolicy"
    targets = [
      {
        id   = data.fmc_device.ftd1.id
        type = "Device"
        name = data.fmc_device.ftd1.name
      }
    ]
}

resource "fmc_ftd_platform_settings_http_access" "http_access" {
    ftd_platform_settings_id = fmc_ftd_platform_settings.platform_settings.id
    server_enabled           = true
    server_port              = var.health_port
    configurations = [
      {
        source_network_object_id = fmc_network.app_subnet.id
        interface_objects = [
          {
              id   = fmc_security_zone.inside_sz.id
              name = "${local.env_name}-Inside-sz"
              type = "SecurityZone"
          }
        ]
      }
    ]
}

resource "fmc_device_deploy" "ftd-deploy-changed" {
    depends_on = [
        fmc_device_physical_interface.outside_int,
        fmc_device_physical_interface.inside_int,
        fmc_device_ipv4_static_route.inside_static_route,
        fmc_device_vni_interface.vni_int,
        fmc_ftd_platform_settings_http_access.http_access,
        fmc_policy_assignment.platform_policy_assignment
    ]
    device_id_list = [data.fmc_device.ftd1.id]
    ignore_warning = false
}
