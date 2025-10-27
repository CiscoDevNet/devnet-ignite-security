# App Resources

# App AMI
data "aws_ami" "ami_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm*"]
  }
  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

# App interface
resource "aws_network_interface" "app_if" {
  subnet_id       = aws_subnet.app_subnet.id
  security_groups = [aws_security_group.app_security_group.id]
  private_ip    = var.app_server
  tags = {
    Name = "${local.env_name}-app-if"
  }
}

# Instances in App VPC
resource "aws_instance" "app" {
  ami           = data.aws_ami.ami_linux.id
  instance_type = "t3a.micro"
  key_name      = aws_key_pair.public_key.key_name
  network_interface {
    network_interface_id = aws_network_interface.app_if.id
    device_index         = 0
  }
  tags = {
    Name = "${local.env_name}-app-instance"
  }
}

# AWS Elastic IP
resource "aws_eip" "app-EIP" {
  depends_on = [aws_internet_gateway.app_igw, aws_instance.app]
  tags = {
    Name = "${local.env_name}-app"
    app  = "service"
  }
}

# AWS Elastic IP to Management IP association
resource "aws_eip_association" "app-ip-assocation" {
  network_interface_id = aws_network_interface.app_if.id
  allocation_id        = aws_eip.app-EIP.id
}

resource "local_file" "lab_info" {
    depends_on = [aws_eip.ftd-mgmt-EIP, aws_instance.app]
    content     = <<-EOT
    FTD SSH  = ssh -o "StrictHostKeyChecking no" -i "${local_file.this.filename}" admin@${aws_eip.ftd-mgmt-EIP.public_dns}
    APP SSH  = ssh -o "StrictHostKeyChecking no" -i "${local_file.this.filename}" ec2-user@${aws_instance.app.public_dns}
    EOT

    filename = "${path.module}/lab_info.txt"
}
