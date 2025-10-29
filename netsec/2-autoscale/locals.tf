###########
# Locals
###########

# Env name is tagged on all resources
locals {
  env_name = "DevNet-Ignite-${var.env_pod_number}"
  ftd_device_group = "DevNet-AutoScale-${var.env_pod_number}"
}

