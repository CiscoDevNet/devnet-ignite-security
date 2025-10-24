# TODO talk about FTD snapshotting within the AMI

# FTD Resources

# populating the FTDv Startup File
# some of these values are populated by the FMC
data "template_file" "ftd_startup_file" {
  template = file("${path.module}/ftd_startup_file.json")
  vars = {
    ftd_hostname       = "${var.env_name}-FTDv"
    fmc_reg_key        = "${sccfm_ftd_device.ftd1.reg_key}"
    fmc_nat_id         = "${sccfm_ftd_device.ftd1.nat_id}"
    ftd_admin_password = random_password.ftd_pass.result
    fmc_hostname       = "${sccfm_ftd_device.ftd1.hostname}"
  }
}

# FTD AMI
data "aws_ami" "ftdv" {
  owners      = ["aws-marketplace"]
  most_recent = true
  filter {
    name   = "name"
    values = ["*${var.ftdv_version}*"]
  }
  filter {
    name   = "product-code"
    values = ["a8sxy6easi2zumgtyr564z6y7"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# FTD Management interface
resource "aws_network_interface" "ftd_management" {
  description     = "ftd_mgmt_if"
  subnet_id       = aws_subnet.mgmt_subnet.id
  security_groups = [aws_security_group.allow_egress_ingress_ssh.id]
  private_ips   = [var.ftd_mgmt_private_ip]
  tags = {
    Name = "${var.env_name}-FTDv-mgmt"
  }
}

# FTD Diagnostic interface
resource "aws_network_interface" "ftd_diagnostic" {
  description     = "ftd_diag_if"
  subnet_id       = aws_subnet.mgmt_subnet.id
  security_groups = [aws_security_group.allow_all.id]
  tags = {
    Name = "${var.env_name}-FTDv-diag-interface-1"
  }
}

# FTD Inside interface
resource "aws_network_interface" "ftd_inside" {
  description       = "ftd_inside_if"
  subnet_id         = aws_subnet.inside_subnet.id
  security_groups   = [aws_security_group.allow_all.id]
  source_dest_check = false
  tags = {
    Name = "${var.env_name}-FTDv-data-interface-2"
  }
}

# FTD Outside interface
resource "aws_network_interface" "ftd_outside" {
  description       = "ftd_outside_if"
  subnet_id         = aws_subnet.outside_subnet.id
  security_groups   = [aws_security_group.allow_all.id]
  source_dest_check = false
  tags = {
    Name = "${var.env_name}-FTDv-data-interface-3"
  }
}

# FTD Firewalls

# since we don't need to manually log into the FTDv firewall in AWS (use pubkey), password is unimportant
resource "random_password" "ftd_pass" {
  length           = 10
  min_lower        = 1
  min_numeric      = 1
  min_special      = 1
  min_upper        = 1
}

resource "aws_instance" "ftdv" {
  ami           = data.aws_ami.ftdv.id
  instance_type = var.ftdv_instance_size
  key_name      = aws_key_pair.public_key.id
  metadata_options {
    http_endpoint = "enabled"
  }
  root_block_device {
    encrypted = true
  }
  network_interface {
    network_interface_id = aws_network_interface.ftd_management.id # ftd_management
    device_index         = 0
  }
  network_interface {
    network_interface_id = aws_network_interface.ftd_diagnostic.id # ftd_diagnostic
    device_index         = 1
  }
  network_interface {
    network_interface_id = aws_network_interface.ftd_inside.id # ftd_inside
    device_index         = 2
  }
  network_interface {
    network_interface_id = aws_network_interface.ftd_outside.id # ftd_outside
    device_index         = 3
  }
  # optional DMZ interface
  # dynamic "network_interface" {
  #   for_each = var.dmz_subnet == null ? toset([]) : toset([1])

  #   content {
  #     network_interface_id = aws_network_interface.ftd_dmz[0].id
  #     device_index         = 4
  #   }
  # }
  user_data = data.template_file.ftd_startup_file.rendered
  tags = {
    Name = "${var.env_name}-FTDv"
  }

  lifecycle {
    ignore_changes = [ami]
  }
}

# AWS Elastic IP
resource "aws_eip" "ftd-mgmt-EIP" {
  depends_on = [aws_internet_gateway.mgmt_igw, aws_instance.ftdv]
  tags = {
    Name = "${var.env_name}-FTDv"
    app  = "service"
  }
}

# AWS Elastic IP to Management IP association
resource "aws_eip_association" "ftd-mgmt-ip-assocation" {
  network_interface_id = aws_network_interface.ftd_management.id
  allocation_id        = aws_eip.ftd-mgmt-EIP.id
}
