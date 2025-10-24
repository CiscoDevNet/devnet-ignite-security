# Service VPC
resource "aws_vpc" "service_vpc" {
  cidr_block           = var.service_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  instance_tenancy     = "default"
  tags = {
    Name = "${var.env_name}"
  }
}

# Service Subnets
resource "aws_subnet" "mgmt_subnet" {
  vpc_id            = aws_vpc.service_vpc.id
  cidr_block        = var.mgmt_subnet
  availability_zone = var.aws_az
  tags = {
    Name = "${var.env_name}-mgmt"
  }
}
resource "aws_subnet" "outside_subnet" {
  vpc_id            = aws_vpc.service_vpc.id
  cidr_block        = var.outside_subnet
  availability_zone = var.aws_az
  tags = {
    Name = "${var.env_name}-outside"
  }
}
resource "aws_subnet" "inside_subnet" {
  vpc_id            = aws_vpc.service_vpc.id
  cidr_block        = var.inside_subnet
  availability_zone = var.aws_az
  tags = {
    Name = "${var.env_name}-inside"
  }
}
# Service Mgmt Internet Gateway
resource "aws_internet_gateway" "mgmt_igw" {
  vpc_id = aws_vpc.service_vpc.id
  tags = {
    Name = "${var.env_name}-mgmt-igw"
  }
}

# Mgmt Route Table
resource "aws_route_table" "mgmt_route_table" {
  vpc_id = aws_vpc.service_vpc.id
  tags = {
    Name = "${var.env_name}-mgmt-rt"
  }
}

# Mgmt Default Route Routes
resource "aws_route" "mgmt_default_route" {
  depends_on = [aws_internet_gateway.mgmt_igw]
  route_table_id         = aws_route_table.mgmt_route_table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.mgmt_igw.id
}

# Mgmt Route Associations
resource "aws_route_table_association" "mgmt_association" {
  subnet_id      = aws_subnet.mgmt_subnet.id
  route_table_id = aws_route_table.mgmt_route_table.id
}


# Application VPC
resource "aws_vpc" "app_vpc" {
  cidr_block           = var.app_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  instance_tenancy     = "default"
  tags = {
    Name = "${var.env_name}-app-vpc"
  }
}

# App Subnets
resource "aws_subnet" "gwlbe_subnet" {
  vpc_id            = aws_vpc.app_vpc.id
  cidr_block        = var.gwlbe_subnet
  availability_zone = var.aws_az
  tags = {
    Name = "${var.env_name}-gwlbe-subnet"
  }
}
resource "aws_subnet" "app_subnet" {
  vpc_id            = aws_vpc.app_vpc.id
  cidr_block        = var.app_subnet
  availability_zone = var.aws_az
  tags = {
    Name = "${var.env_name}-app-subnet"
  }
}

# App Internet Gateway
resource "aws_internet_gateway" "app_igw" {
  vpc_id = aws_vpc.app_vpc.id
  tags = {
    Name = "${var.env_name}-app-igw"
  }
}

# Lambda Subnet

resource "aws_subnet" "lambda_subnet" {
  count             = 1
  vpc_id            = aws_vpc.service_vpc.id
  cidr_block        = var.lambda_subnet
  availability_zone = var.aws_az
  tags = {
    Name = "${var.env_name}-lambda-subnet"
  }
}

resource "aws_eip" "lambda_nat_gateway_eip" {
  count = 1
  tags = {
    Name = "${var.env_name}-lambda-eip"
  }
}

resource "aws_nat_gateway" "lambda_nat_gateway" {
  count         = 1
  allocation_id = aws_eip.lambda_nat_gateway_eip[0].id
  subnet_id     = aws_subnet.mgmt_subnet.id
  tags = {
    Name = "${var.env_name}-lambda-natgw"
  }
}

resource "aws_route_table" "lambda_route_table" {
  count = 1
  vpc_id = aws_vpc.service_vpc.id
  tags = {
    Name = "${var.env_name}-lambda-rt"
  }
}

resource "aws_route" "lambda_nat_route" {
  count = 1
  route_table_id         = aws_route_table.lambda_route_table[0].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.lambda_nat_gateway[0].id
}

resource "aws_route_table_association" "lambda_private_subnet_association" {
  count          = 1
  subnet_id      = aws_subnet.lambda_subnet[0].id
  route_table_id = aws_route_table.lambda_route_table[0].id
}

# Security Groups

locals {
  ingress_networks = concat(["10.0.0.0/8"], var.ingress_user_networks)
}

# Service Security VPC
resource "aws_security_group" "allow_egress_ingress_ssh" {
  name        = "Allow All Egress Inbound SSH"
  description = "Allow all egress, Inbound SSH"
  vpc_id      = aws_vpc.service_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "6"
    cidr_blocks = local.ingress_networks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.env_name}-service-sg"
    app  = "service"
  }
}

resource "aws_security_group" "allow_all" {
  name        = "Allow All"
  description = "Allow all"
  vpc_id      = aws_vpc.service_vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.env_name}-service-sg-allow-all"
    app  = "service"
  }
}

# Allow All - Application VPC
resource "aws_security_group" "app_security_group" {
  name        = "Allow Inbound SSH"
  description = "Allow Inbound SSH"
  vpc_id      = aws_vpc.app_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "6"
    cidr_blocks = local.ingress_networks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.env_name}-app-sg"
    app  = "service"
  }
}

