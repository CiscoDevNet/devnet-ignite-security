###################################
# Providers
###################################

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
        fmc = {
      source = "CiscoDevNet/fmc"
      version = "2.0.0-rc1"
    }
    sccfm = {
      source = "CiscoDevnet/sccfm"
    }
  }
}

provider "aws" {
  region     = var.region
}

provider "fmc" {
  url = "https://api.us.security.cisco.com/firewall/v1/cdfmc"
  #token = "" use FMC_TOKEN environment variable
  token = var.sccfm_api_token
}

provider "sccfm" {
  # export TF_VAR_sccfm_api_token=yourtokenhere
  base_url  = "https://www.defenseorchestrator.com"
  api_token = var.sccfm_api_token
  #api_token = local.api_token
}
