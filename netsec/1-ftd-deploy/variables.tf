##############
# Variables
##############

# Env POD number
variable "env_pod_number" {
  # Specified as an environment variable in the lab
  type = number
  validation {
    condition     = can(regex("^[0-9]{3}$", var.env_pod_number))
    error_message = "The pod number must be exactly three digits (0-9)."
  }
}

variable "ingress_user_networks" {
    default = ["IPADDRESS/32"]
}

variable "region" {
  type          = string
  default       = "us-east-2"
}
variable "aws_az" {
  type          = string
  default       = "us-east-2a"
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
variable "ccl_subnet" {
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

variable "ftdv_performance_tier" {
  type          = string
  default       = "FTDv5"
}

variable "ftdv_mgmt_private_ip" {
  type          = string
  default       = "0.0.0.0"
}

# API Key for cdFMC and SCC
variable "sccfm_api_token" {
  type          = string 
}

# AWS Access Key
variable "aws_access_key_id" {
  type          = string
}

# AWS Secret Access Key
variable "aws_secret_access_key" {
  type          = string
  sensitive     = true
}
