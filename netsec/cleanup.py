import sys
import os
import json
import boto3
import requests
import argparse
from pprint import pprint

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

VERBOSE = 0
SCC_API = 'api.us.security.cisco.com'
ITERATION_COUNT = 10

region = 'us-east-1'
pod = '123'
tag_match = f'DevNet-Ignite-{pod}'
    
def print_all(item):
    if VERBOSE:
        pprint(item) 

class AwsPod:

    def __init__(self, region, tag_name, pod_number, delete=False):
        api_token = os.getenv('FMC_TOKEN')
        if os.getenv('AWS_ACCESS_KEY_ID') is None or os.getenv('AWS_SECRET_ACCESS_KEY') is None:
            print("AWS init Error: please provide AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY for AWS as env variables")
            exit(1)
        self.region = region
        self.tag_name = tag_name
        self.pod_number = pod_number
        self.delete = delete
        self.tag_match = f'{tag_name}-{pod_number}'
        self.ec2_client = boto3.client('ec2', region_name = region)
        self.elbv2_client = boto3.client('elbv2', region_name = region)
        self.cf_client = boto3.client('cloudformation', region_name=region)


        self.name_filter = [
            {
                'Name' : 'tag:Name',
                'Values' : [
                    f'{self.tag_match}*',
                ],
            },
        ]

    def run_all(self):
        try:
            self.del_instances()
            self.del_interfaces()
            self.del_cloudformation_stack()
            self.del_gateway_lb_resources()
            self.del_load_balancers()
            self.del_eips()
            self.del_vpcs()
            self.del_key_pair()
        except boto3.exceptions.Boto3Error as e:
            print(e)
            exit(1)
        

    def get_name_values(self, tag_dict, value):
        return ','.join([i['Value'] for i in tag_dict['Tags'] if i['Key'] == 'Name' and value in i['Value']])
    
    def del_vpcs(self):
        client = self.ec2_client
        vpcs = client.describe_vpcs(Filters=self.name_filter)
        print_all(vpcs)
        for vpc in vpcs['Vpcs']:
            vpc_id = vpc['VpcId'] 
            print("VPC Id: " + vpc_id + " Name: " + self.get_name_values(vpc, self.tag_match))

            nat_gateways = client.describe_nat_gateways(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
            for nat_gw in nat_gateways['NatGateways']:
                print(f"    NAT Gateway: {nat_gw['NatGatewayId']}")
                if self.delete:
                    client.delete_nat_gateway(NatGatewayId=nat_gw['NatGatewayId'])
                    waiter = client.get_waiter('nat_gateway_deleted')
                    waiter.wait(NatGatewayIds=[nat_gw['NatGatewayId']])

            eips = client.describe_addresses()
            for eip in eips['Addresses']:
                if 'VpcId' in eip and eip['VpcId'] == vpc_id:
                    allocation_id = eip['AllocationId']
                    print(f"    EIPs: Public IP {eip['PublicIp']} Allocation ID {allocation_id}")
                    if self.delete:
                        client.release_address(AllocationId=allocation_id)

            internet_gateways = client.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])
            for igw in internet_gateways['InternetGateways']:
                print(f"    Internet Gateway: {igw['InternetGatewayId']}")
                if self.delete:
                    client.detach_internet_gateway(InternetGatewayId=igw['InternetGatewayId'], VpcId=vpc_id)
                    client.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])

            endpoints = client.describe_vpc_endpoints(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
            for ep in endpoints['VpcEndpoints']:
                print(f"    VPC endpoint: {ep['VpcEndpointId']}")
                if self.delete:
                    client.delete_vpc_endpoints(VpcEndpointIds=[ep['VpcEndpointId']])
            
            try:
                subnets = client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
                for subnet in subnets['Subnets']:
                    print(f"    subnet: {subnet['SubnetId']}")
                    if self.delete:
                        client.delete_subnet(SubnetId=subnet['SubnetId'])
            except Exception as e:
                print(f"Error deleting subnet: {e}")

            try:
                security_groups = client.describe_security_groups(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
                for sg in security_groups['SecurityGroups']:
                    if sg['GroupName'] != 'default':
                        print(f"    security group: {sg['GroupId']} ({sg['GroupName']})")
                        if self.delete:
                            client.delete_security_group(GroupId=sg['GroupId'])
            except Exception as e:
                print(f"Error deleting security group: {e}")

            try:
                route_tables = client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
                for rt in route_tables['RouteTables']:
                    is_main = False
                    for association in rt['Associations']:
                        if association.get('Main'):
                            is_main = True
                            break
                    if not is_main:
                        print(f"    route table: {rt['RouteTableId']}")
                        if self.delete:
                            client.delete_route_table(RouteTableId=rt['RouteTableId'])
            except Exception as e:
                print(f"Error deleting security group: {e}")

            try:
                network_acls = client.describe_network_acls(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
                for nacl in network_acls['NetworkAcls']:
                    if not nacl['IsDefault']:
                        print(f"    Network ACL: {nacl['NetworkAclId']}")
                        if self.delete:
                            client.delete_network_acl(NetworkAclId=nacl['NetworkAclId'])
            except Exception as e:
                print(f"Error deleting security group: {e}")
            if self.delete:
                try:
                    client.delete_vpc(VpcId=vpc_id)
                except Exception as e:
                    print(f"Error deleting security group: {e}")

    def del_eips(self):
        client = self.ec2_client
        eips = client.describe_addresses(Filters=self.name_filter)
        for eip in eips['Addresses']:
                allocation_id = eip['AllocationId']
                print(f"    EIPs: Public IP {eip['PublicIp']} Allocation ID {allocation_id}")
                if self.delete:
                    try:
                        response = client.release_address(AllocationId=allocation_id)
                        if response.get('Unsuccessful'):
                            for item in response['Unsuccessful']:
                                print(f"  Error deleting EIP {item.get('ResourceId')}: {item.get('Error', {}).get('Message')}")
                    except Exception as e:
                        print(f"Error deleting EIP {eip['PublicIp']}: {e}")
    
    def del_load_balancers(self):
        client = self.elbv2_client
        response = client.describe_load_balancers()
        lb_list = []
        for lb in response['LoadBalancers']:
            lb_arn = lb['LoadBalancerArn']
            tags_response = client.describe_tags(ResourceArns=[lb_arn])
            for tag_desc in tags_response['TagDescriptions']:
                for tag in tag_desc['Tags']:
                    if tag['Key'] == 'Name' and tag_match in tag['Value']:
                        lb_list.append(lb)
        for lb in lb_list:
            try:
                lb_arn = lb['LoadBalancerArn']
                print(f"Load Balancer: {lb['LoadBalancerName']} {lb_arn}")

                response = client.describe_listeners(LoadBalancerArn=lb_arn)
                for listener in response['Listeners']:
                    listener_arn = listener['ListenerArn']
                    print(f"Listener: {listener_arn}")
                    if self.delete:
                        client.delete_listener(ListenerArn=listener_arn)
                        print(f"Listener {listener_arn} deleted successfully.")

                response = client.describe_target_groups(LoadBalancerArn=lb_arn)
                for tg in response['TargetGroups']:
                    tg_arn = tg['TargetGroupArn']
                    print(f"Target Group: {tg['TargetGroupName']} (ARN: {tg['TargetGroupArn']})")
                    if self.delete:
                        client.delete_target_group(TargetGroupArn=tg['TargetGroupArn'])
                        print(f"Target Group {tg_arn} deleted successfully.")
                if self.delete:
                    client.delete_load_balancer(LoadBalancerArn=lb_arn)
                    print(f"Loadbalancer {lb_arn} deleted successfully.")
            except Exception as e:
                print(f"Error deleting Loadbalancer: {e}")
    
    def del_gateway_lb_resources(self):
        client = self.ec2_client

        # delete vpc service route table entry
        try:
            response = client.describe_route_tables(
                Filters=[{'Name': 'tag:Name', 'Values': [f'{self.tag_match}*']}]
            )
            route_tables = response.get('RouteTables', [])
            for rt in route_tables:
                for route in rt['Routes']:
                    if route.get('GatewayId', "").startswith('vpce-'):
                        destination_cidr_block = route.get('DestinationCidrBlock')
                        print(f"Found route to delete: DestinationCidrBlock={destination_cidr_block}")
                        if destination_cidr_block:
                            client.delete_route(
                                RouteTableId=rt['RouteTableId'],
                                DestinationCidrBlock=destination_cidr_block
                            )
                            print(f"Successfully deleted route for endpoint service from route table.")
                            return
                        else:
                            print("Could not determine DestinationCidrBlock for the route to delete.")
                            return
        except Exception as e:
            print(f"An error occurred deleting vpc service route table: {e}")

        response = client.describe_vpc_endpoints(
            Filters=[
                {'Name': 'vpc-endpoint-type', 'Values': ['GatewayLoadBalancer']},
                {'Name': 'tag:Name', 'Values': [f'{self.tag_match}*']}
            ]
        )
        vpc_endpoint_ids = []
        for endpoint in response['VpcEndpoints']:
            print(f"Found GWLB Endpoint: {endpoint['VpcEndpointId']} (Service Name: {endpoint.get('ServiceName')})")
            try:
                vpc_endpoint_ids.append(endpoint['VpcEndpointId'])
                if self.delete:
                    response = client.delete_vpc_endpoints(VpcEndpointIds=[endpoint['VpcEndpointId']])
                    if response.get('Unsuccessful'):
                        print("Deletion was unsuccessful for some services:")
                        for item in response['Unsuccessful']:
                            print(f"  Error deleting {item.get('ResourceId')}: {item.get('Error', {}).get('Message')}")
                    else:
                        print("Deleted GWLB Endpoint")
            except Exception as e:
                print(f"Error deleting endpoint: {e}")

        response = client.describe_vpc_endpoint_services(
            Filters=[
                {'Name': 'service-type', 'Values': ['GatewayLoadBalancer']},
                {'Name': 'tag:Name', 'Values': [f'{self.tag_match}*']}
            ]
        )
        for service in response['ServiceDetails']:
            print(f"Found GWLB Endpoint Service: {service['ServiceName']} (Service ID: {service['ServiceId']})")
            if self.delete:
                try:
                    for endpoint in vpc_endpoint_ids:
                        response = client.reject_vpc_endpoint_connections(
                            ServiceId=service['ServiceId'],
                            VpcEndpointIds=[endpoint]
                        )
                        unsuccessful = response.get('Unsuccessful')
                        if unsuccessful:
                            print(f"Failed to reject some endpoint connections:")
                            for entry in unsuccessful:
                                print(f"  Endpoint ID: {entry.get('ResourceId')}, {entry.get('Error', {}).get('Message')}")
                        else:
                            print(f"Successfully rejected endpoint connections for service {service['ServiceId']}.")
                    response = client.delete_vpc_endpoint_service_configurations(ServiceIds=[service['ServiceId']])
                    print(f"Successfully initiated deletion for endpoint service: {service['ServiceId']}")
                    if response.get('Unsuccessful'):
                        print("Deletion was unsuccessful for some services:")
                        for item in response['Unsuccessful']:
                            print(f"  Error deleting {item.get('ResourceId')}: {item.get('Error', {}).get('Message')}")
                except Exception as e:
                    print(f"Error deleting endpoint service {service['ServiceId']}: {e}")

        client = self.elbv2_client
        response = client.describe_target_groups()
        for tg in response['TargetGroups']:
            tg_arn = tg['TargetGroupArn']
            tags_response = client.describe_tags(ResourceArns=[tg_arn])
            for tag_desc in tags_response['TagDescriptions']:
                for tag in tag_desc['Tags']:
                    if tag['Key'] == 'Name' and tag_match in tag['Value']:
                        print(f"Target Group: {tg['TargetGroupName']} (ARN: {tg['TargetGroupArn']})")
                        if self.delete:
                            client.delete_target_group(TargetGroupArn=tg['TargetGroupArn'])
                            print(f"Target Group {tg_arn} deleted successfully.")

    def del_instances(self):
        client = self.ec2_client
        response = client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [f'{self.tag_match}*']
                }
            ]
        )
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:

                if self.delete:
                    client.terminate_instances(InstanceIds=[instance['InstanceId']])

    def del_interfaces(self):
        client = self.ec2_client
        interfaces = client.describe_network_interfaces(Filters=self.name_filter)
        for interface in interfaces['NetworkInterfaces']:
            eni_id = interface['NetworkInterfaceId']
            print(f"ENI: {eni_id}")
            if 'Association' in interface and 'AllocationId' in interface['Association']:
                allocation_id = interface['Association']['AllocationId']
                print(f"    Elastic IP with Allocation ID: {allocation_id}")
                if self.delete:
                    client.disassociate_address(AssociationId=interface['Association']['AssociationId'])
                    client.release_address(AllocationId=allocation_id)
            if 'Attachment' in interface and interface['Attachment']['Status'] == 'in-use':
                attachment_id = interface['Attachment']['AttachmentId']
                print(f"  Interface is attached (Attachment ID: {attachment_id})")
                if self.delete:
                    client.detach_network_interface(
                        AttachmentId=attachment_id,
                    )
                    time.sleep(5) 
            try:
                if self.delete:
                    client.delete_network_interface(NetworkInterfaceId=eni_id)
            except client.exceptions.ClientError as e:
                if "InvalidNetworkInterfaceID.NotFound" in str(e):
                    print(f"Network Interface {eni_id} already deleted or not found.")
                elif "InvalidParameterValue" in str(e) and "is currently in use" in str(e):
                    print(f"Network Interface {eni_id} is still in use and cannot be deleted yet. It might be associated with a terminating instance.")
                else:
                    print(f"Error deleting Network Interface {eni_id}: {e}")

    def del_key_pair(self):
        client = self.ec2_client
        response = client.describe_key_pairs()
        for key_pair in response['KeyPairs']:
            tags = key_pair.get('Tags', [])
            for tag in tags:
                if tag['Key'] == 'Name' and self.tag_match in tag['Value']:
                    print(f"Key pair: {key_pair['KeyName']}")
                    if self.delete:
                        client.delete_key_pair(KeyName=key_pair['KeyName'])

    def del_cloudformation_stack(self):
        client = self.cf_client
        response = client.list_stacks()
        for stack in response['StackSummaries']:
            if stack['StackStatus'] in ['DELETE_COMPLETE', 'DELETE_IN_PROGRESS']:
                continue
            if self.tag_match in stack['StackName']:
                print(f"Stack: {stack['StackName']}")
                if self.delete:
                    client.delete_stack(StackName=stack['StackName'])
            else:
                return
            
            if not self.delete:
                continue
            print(f"Stack deletion initiated for {stack['StackName']}. Waiting for completion...")
            
            try:
                waiter = client.get_waiter('stack_delete_complete')
                waiter.config.max_attempts = 2
                waiter.wait(StackName=stack['StackName'])
                print(f"CloudFormation stack '{stack['StackName']}' deleted successfully.")
            except Exception as e:
                print(f"CloudFormation stack '{stack['StackName']}' still being deleted... moving on...")

    def del_elastic_ips(self):
        client = self.ec2_client
        response = client.describe_addresses()
        for eip in response['Addresses']:
            if 'Tags' in eip:
                for tag in eip['Tags']:
                    if tag['Key'] == 'Name' and self.tag_match in tag['Value']:
                        allocation_id = eip['AllocationId']
                        public_ip = eip['PublicIp']
                        print(f"Found EIP with Public IP: {public_ip} and Allocation ID: {allocation_id}")
                        if self.delete:
                            client.release_address(AllocationId=allocation_id)
                        break


class SccPod:

    def __init__(self, tag_name, pod_number, delete=False):
        api_token = os.getenv('FMC_TOKEN')
        if api_token is None:
            print("SCC init Error: please provide api_token for SCC in env variable FMC_TOKEN")
            exit(1)
        self.scc_server = f"https://{SCC_API}"
        self.server = self.scc_server + '/firewall/v1/cdfmc'
        self.api_token = api_token
        self.headers = {'Authorization': f"Bearer {self.api_token}", 'Content-Type': 'application/json'}
        self.tag_match = f'{tag_name}-{pod_number}'
        self.delete = delete

    def rest_get(self, url):
        try:
            r = requests.get(url, headers=self.headers, verify=False)
            status_code = r.status_code
            if not (200 <= status_code <= 300):
                r.raise_for_status()
                print("Error occurred in Get -->"+r.json())
        except requests.exceptions.HTTPError as err:
            print("Error in connection --> "+str(err))
        finally:
            if r: r.close()
            return r

    def rest_post(self, url, post_data):
        try:
            r = requests.post(url, data=json.dumps(post_data), headers=self.headers, verify=False)
            status_code = r.status_code
            if not (201 <= status_code <= 202):
                print("Error occurred in POST --> "+r.json())
        except requests.exceptions.HTTPError as err:
            print("Error in connection --> "+str(err))
        finally:
            if r: r.close()
            return r

    def rest_delete(self, url):
        try:
            r = requests.delete(url, headers=self.headers, verify=False)
            status_code = r.status_code
            if 200 <= status_code <= 300:
                r.raise_for_status()
                print("Error occurred in Delete -->"+r.json())
        except requests.exceptions.HTTPError as err:
            print("Error in connection --> "+str(err))
        finally:
            if r: r.close()
            return r

    def del_ac_policy(self):
        api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/accesspolicies"
        url = f"{self.server}{api_path}"
        r = self.rest_get(url)
        if 'items' in r.json():
            for item in r.json()['items']:
                if self.tag_match in item['name']:
                    print(f"Found AC policy: {item['name']}")
                    if self.delete:
                        url = f"{self.server}{api_path}/{item['id']}"
                        self.rest_delete(url)

    def del_platform_policy(self):
        api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/ftdplatformsettingspolicies"
        url = f"{self.server}{api_path}"
        r = self.rest_get(url)
        if 'items' in r.json():
            for item in r.json()['items']:
                if self.tag_match in item['name']:
                    print(f"Found Platform policy: {item['name']}")
                    if self.delete:
                        url = f"{self.server}{api_path}/{item['id']}"
                        self.rest_delete(url)

    def del_intrusion_policy(self):
        api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/intrusionpolicies"
        url = f"{self.server}{api_path}"
        r = self.rest_get(url)
        if 'items' in r.json():
            for item in r.json()['items']:
                if self.tag_match in item['name']:
                    print(f"Found Intrusion policy: {item['name']}")
                    if self.delete:
                        url = f"{self.server}{api_path}/{item['id']}"
                        self.rest_delete(url)

    def del_objects(self):
        api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/hosts"
        url = f"{self.server}{api_path}"
        r = self.rest_get(url)
        if 'items' in r.json():
            for item in r.json()['items']:
                if self.tag_match in item['name']:
                    print(f"Found Host Object: {item['name']}")
                    if self.delete:
                        url = f"{self.server}{api_path}/{item['id']}"
                        self.rest_delete(url)

        api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/networks"
        url = f"{self.server}{api_path}"
        r = self.rest_get(url)
        if 'items' in r.json():
            for item in r.json()['items']:
                if self.tag_match in item['name']:
                    print(f"Found Network Object: {item['name']}")
                    if self.delete:
                        url = f"{self.server}{api_path}/{item['id']}"
                        self.rest_delete(url)

        api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/securityzones"
        url = f"{self.server}{api_path}"
        r = self.rest_get(url)
        if 'items' in r.json():
            for item in r.json()['items']:
                if self.tag_match in item['name']:
                    print(f"Found Security Zone: {item['name']}")
                    if self.delete:
                        url = f"{self.server}{api_path}/{item['id']}"
                        self.rest_delete(url)

    def del_devices(self):
        api_path = "/firewall/v1/inventory/devices"
        url = f"{self.scc_server}{api_path}"
        r = self.rest_get(url)
        if 'items' in r.json():
            for item in r.json()['items']:
                if self.tag_match in item['name']:
                    print(f"Found device {item['name']} {item['uid']}")
                    if self.delete:
                        api_path = f"/firewall/v1/inventory/devices/ftds/cdfmcManaged/{item['uid']}/delete"
                        url = f"{self.scc_server}{api_path}"
                        r = self.rest_post(url, "")
    def run_all(self):
        self.del_devices()
        self.del_ac_policy()
        self.del_intrusion_policy()
        self.del_platform_policy()
        self.del_objects()


def main():
    parser = argparse.ArgumentParser(
                    prog='Cleanup',
                    description='Clean up the Terraform AWS and SCC resources of the DevNet Ignite NetSec labs')
    parser.add_argument('-d', '--delete', action='store_true', help="Delete the resources")
    parser.add_argument('-g', '--get', help="Get and print all pods")
    parser.add_argument('-a', '--all', help="Cleanup all pods")
    parser.add_argument('-p', '--pod', help="Cleanup specified pod")
    args = parser.parse_args()

    if args.get:
        pass
    elif args.pod:
        for i in range(1, ITERATION_COUNT + 1):
            if args.delete:
                print(f"\n** Attempt number {i}/{ITERATION_COUNT} **\n")
            scc = SccPod('DevNet-Ignite', args.pod, delete=args.delete)
            scc.run_all()
            pod = AwsPod('us-east-1', 'DevNet-Ignite', args.pod, delete=args.delete)
            pod.run_all()
            if not args.delete:
                break
    elif args.all:
        pass
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
