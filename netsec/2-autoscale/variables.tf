##############
# Variables
##############

# Environment

# Env name is tagged on all resources
variable "env_name" {
  type          = string
  default       = "DevNetBG-Ignite"
}

variable "ingress_user_networks" {
    default = ["151.186.182.0/23", "151.186.192.0/20", "173.38.117.0/24"]
}

# AWS
# variable "aws_access_key" {
#   description   = "Pass this value using tfvars file"
#   type          = string
#   sensitive     = true
# }
# variable "aws_secret_key" {
#   description   = "Pass this value using tfvars file"
#   type          = string
#   sensitive     = true
# }
variable "region" {
  type          = string
  default       = "us-east-1"
}
variable "aws_az" {
  type          = string
  default       = "us-east-1a"
}

# Service VPC
variable "service_cidr" {
  default       = "10.0.0.0/16"
}
variable "mgmt_subnet" {
  default       = "10.0.0.0/24"
}
variable "outside_subnet" {
  default       = "10.0.1.0/24"
}
variable "inside_subnet" {
  default       = "10.0.2.0/24"
}
variable "lambda_subnet" {
  default       = "10.0.3.0/24"
}
variable "ftd_mgmt_private_ip" {
  default       = "10.0.0.10"
}

# App VPC
variable "app_cidr" {
  default       = "10.1.0.0/16"
}
variable "gwlbe_subnet" {
  default       = "10.1.0.0/24"
}
variable "app_subnet" {
  default       = "10.1.1.0/24"
}
variable "app_server" {
  default       = "10.1.1.100"
}


# Firepower Threat Defense
variable "ftdv_instance_size" {
  type          = string
  default       = "c5.xlarge"
}

variable "ftdv_version" {
  type          = string
  default       = "ftdv-7.7*"
}

# variable "ftdv_pass" {
#   type          = string
#   sensitive     = true
# }

variable "ftdv_performance_tier" {
  type          = string
  default       = "FTDv30"
}

variable "ftdv_mgmt_private_ip" {
  type          = string
  default       = "0.0.0.0"
}

variable "ftd_device_group" {
  type          = string
  default       = "DevNet-AutoScale"
}

# API Key for cdFMC and SCC
variable "sccfm_api_token" {
  type          = string 
}

variable "health_port" {
  type          = string
  default       = "7575"
}

# variable "fmc_host" {
#   description   = "FMC Hostname or IP - pass this value using tfvars file"
#   type          = string
# }
