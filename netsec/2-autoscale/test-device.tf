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

# Instances in App VPC
resource "aws_instance" "app" {
  ami           = data.aws_ami.ami_linux.id
  instance_type = "t3a.micro"
  key_name      = aws_key_pair.public_key.key_name
  subnet_id     = aws_subnet.app_subnet.id
  private_ip    = var.app_server
  associate_public_ip_address = true
  vpc_security_group_ids = [
    aws_security_group.app_security_group.id
  ]
  tags = {
    Name = "${local.env_name}-app-instance"
  }
}

resource "local_file" "lab_info" {
    depends_on = [aws_eip.ftd-mgmt-EIP, aws_instance.app]
    content     = <<-EOT
    FTD SSH  = ssh -o "StrictHostKeyChecking no" -i "${local_file.this.filename}" admin@${aws_eip.ftd-mgmt-EIP.public_dns}
    APP SSH  = ssh -o "StrictHostKeyChecking no" -i "${local_file.this.filename}" ec2-user@${aws_instance.app.public_dns}
    EOT

    filename = "${path.module}/lab_info.txt"
}
