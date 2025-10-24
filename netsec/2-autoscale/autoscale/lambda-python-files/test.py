from fmc import DerivedFMC
from pprint import pprint
import os
import requests
api_token = os.getenv('FMC_TOKEN')
headers = {"Authorization": f"Bearer {api_token}"}
r = requests.get("https://api.us.security.cisco.com/firewall/v1/inventory/devices", headers=headers, verify=False)
print(r.text)
fmc = DerivedFMC("api.us.security.cisco.com", "", "", api_token, "testme")
#fmc.onboard_device_scc("testme", "0ad7f04b-0791-0ed3-0000-004294967299", ["BASE"], "FTDv10")
fmc.update_fmc_config_user_input(
    "DevNet-AutoScale",
    "DevNetBG-Ignite-Access-Policy",
    ["DevNetBG-Ignite-Inside-sz", "DevNetBG-Ignite-Outside-sz"],
    None,
    "App",
    None
)
fmc.set_fmc_configuration(True, "SINGLE_ARM")
config = fmc.check_fmc_configuration(True, "SINGLE_ARM")
print(config)
print(fmc.configuration_status)
pprint(fmc.configuration)
pprint(fmc.add_member_in_device_grp("DevNetBG-Ignite-FTDv", "DevNet-AutoScale", "6d18e3bc-97f0-11f0-85f2-33cb6f4005d5"))
