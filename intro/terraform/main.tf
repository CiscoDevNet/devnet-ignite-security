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
