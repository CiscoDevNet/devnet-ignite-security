# Gateway Load Balancing

# Gateway Load Balancing related resources
resource "aws_lb" "gwlb" {
  name                             = "${local.env_name}-gwlb"
  load_balancer_type               = "gateway"
  subnets                          = [aws_subnet.inside_subnet.id]
  enable_cross_zone_load_balancing = true

  tags = {
    Name = "${local.env_name}-gwlb"
    app  = "service"
  }
}

# Target group is IP based since FTD's are provisioned with multiple interfaces
resource "aws_lb_target_group" "ftd" {
  name        = "${local.env_name}-ftdtg"
  protocol    = "GENEVE"
  vpc_id      = aws_vpc.service_vpc.id
  target_type = "ip"
  port        = 6081
  stickiness {
    type = "source_ip_dest_ip"
  }
  health_check {
    port     = var.health_port
    protocol = "TCP"
  }
  tags = {
    Name = "${local.env_name}-lbtg"
    app  = "service"
  }
}

# Target group is attached to IP address of data interfaces
resource "aws_lb_target_group_attachment" "ftd" {
  target_group_arn = aws_lb_target_group.ftd.arn
  target_id        = aws_network_interface.ftd_inside.private_ip
}


# GWLB Listener
resource "aws_lb_listener" "cluster" {
  load_balancer_arn = aws_lb.gwlb.arn
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ftd.arn
  }
  tags = {
    Name = "${local.env_name}-gwlb-listener"
    app  = "service"
  }
}

# Endpoint Service
resource "aws_vpc_endpoint_service" "gwlb" {
  acceptance_required        = false
  gateway_load_balancer_arns = [aws_lb.gwlb.arn]
  tags = {
    Name = "${local.env_name}-gwlb"
    app  = "service"
  }
}

# GWLB Endpoints. One is required for each AZ in App VPC
resource "aws_vpc_endpoint" "fw" {
  service_name      = aws_vpc_endpoint_service.gwlb.service_name
  vpc_endpoint_type = aws_vpc_endpoint_service.gwlb.service_type
  vpc_id            = aws_vpc.app_vpc.id
  tags = {
    Name = "${local.env_name}-gwlbe"
  }
}

# Delay after GWLB Endpoint creation
# resource "time_sleep" "fw" {
#   create_duration = "180s"
#   depends_on = [
#     aws_vpc_endpoint.fw
#   ]
# }

# GWLB Endpoints are placed in FW Data subnets in Firewall VPC
resource "aws_vpc_endpoint_subnet_association" "fw" {
  vpc_endpoint_id = aws_vpc_endpoint.fw.id
  subnet_id       = aws_subnet.gwlbe_subnet.id
}


# Routing

# App Route Table
resource "aws_route_table" "app_route_table" {
  vpc_id = aws_vpc.app_vpc.id
  tags = {
    Name = "${local.env_name}-app-rt"
  }
}

# App Default route to GWLB Endpoint
resource "aws_route" "app_default_route" {
  depends_on = [aws_vpc_endpoint.fw, aws_vpc_endpoint_subnet_association.fw]
  route_table_id         = aws_route_table.app_route_table.id
  destination_cidr_block = "0.0.0.0/0"
  vpc_endpoint_id        = aws_vpc_endpoint.fw.id
}

# App Subnet Route Association to App Route Table
resource "aws_route_table_association" "app_association" {
  subnet_id      = aws_subnet.app_subnet.id
  route_table_id = aws_route_table.app_route_table.id
}

# GWLBe Subnet Routing

# GWLBe Route Table
resource "aws_route_table" "gwlbe_route_table" {
  vpc_id = aws_vpc.app_vpc.id
  tags = {
    Name = "${local.env_name}-gwlb-rt"
  }
}

# GWLBe Default route to Internet Gateway
resource "aws_route" "gwlbe_default_route" {
  depends_on = [aws_internet_gateway.app_igw]
  route_table_id         = aws_route_table.gwlbe_route_table.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.app_igw.id
}

# GWLBe Subnet Route Associations to GWLBe Route Table
resource "aws_route_table_association" "gwlbe_association" {
  subnet_id      = aws_subnet.gwlbe_subnet.id
  route_table_id = aws_route_table.gwlbe_route_table.id
}

# App IGW Routing

# App IGW Route Table
resource "aws_route_table" "app_igw_route_table" {
  vpc_id = aws_vpc.app_vpc.id
  tags = {
    Name = "${local.env_name}-app-igw-rt"
  }
}

# App IGW route to App Subnet via GWLBe
resource "aws_route" "app_igw_route_app_subnet" {
  depends_on = [aws_vpc_endpoint.fw, aws_vpc_endpoint_subnet_association.fw]
  route_table_id         = aws_route_table.app_igw_route_table.id
  destination_cidr_block = var.app_subnet
  vpc_endpoint_id        = aws_vpc_endpoint.fw.id
}

# App IGW Associations to App IGW Route Table
resource "aws_route_table_association" "app_igw_association" {
  gateway_id     = aws_internet_gateway.app_igw.id
  route_table_id = aws_route_table.app_igw_route_table.id
}
