terraform {
  required_providers {
    fmc = {
      source = "CiscoDevNet/fmc"
      version = "2.0.0-rc2"
    }
  }
}

# cdFMC
provider "fmc" {
  token = var.cdo_token
  url = "https://${var.cdFMC}"
}

# Objects
data "fmc_port" "https" {
  name = "HTTPS"
}

resource "fmc_port" "tcp_8888" {
  port        = "8888"
  name        = "${var.name}_web_app"
  protocol    = "TCP"
  description = "${var.name}_Web Application Service"
}

resource "fmc_host" "app_host" {
  name        = "${var.name}_app_host"
  description = "${var.name}_application container"
  ip          = "10.10.10.10"
  overridable = true
}
resource "fmc_host" "db_host" {
  name        = "${var.name}_db_host"
  description = "${var.name}_database instance"
  ip          = "20.20.20.20"
  overridable = true
}

# Access Policy
resource "fmc_access_control_policy" "example" {
  name                              = "${var.name}_policy"
  description                       = "${var.name}_Access_Control_Policy"
  default_action                    = "BLOCK"
  default_action_log_begin          = true
  default_action_log_end            = false
  default_action_send_events_to_fmc = true
  categories = [
    {
      name = "${var.name}"
      section = "mandatory"
    }
  ]
  rules = [
    {
      action = "ALLOW"
      name   = "rule_1"
      category_name = "${var.name}"
      source_network_objects = [
        {
          id   = fmc_host.app_host.id
          type = "Host"
        }
      ]
      destination_network_objects = [
        {
          id   = fmc_host.db_host.id
          type = "Host"
        }
      ]
      destination_port_objects = [
        {
          id = data.fmc_port.https.id
        },
        {
          id = fmc_port.tcp_8888.id
        }
      ]
      log_begin           = false
      log_end             = true
      send_events_to_fmc  = true
    }
  ]
}