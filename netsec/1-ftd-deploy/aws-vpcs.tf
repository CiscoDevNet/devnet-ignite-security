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

# Security Groups

# Allow All - Security VPC
resource "aws_security_group" "allow_all" {
  name        = "Allow All"
  description = "Allow all traffic"
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
    Name = "${var.env_name}-service-sg"
    app  = "service"
  }
}

# Allow All - Application VPC
resource "aws_security_group" "app_allow_all" {
  name        = "Allow All"
  description = "Allow all traffic"
  vpc_id      = aws_vpc.app_vpc.id

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
    Name = "${var.env_name}-app-sg"
    app  = "service"
  }
}
