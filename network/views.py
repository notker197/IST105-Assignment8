from django.shortcuts import render
from .forms import NetworkForm
import time
from datetime import datetime
import pymongo

leases = {}

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["dhcp"]
collection = db["leases"]

def generate_ipv4(mac):
    return "192.168.1." + str(int(mac[-2:], 16) % 255)

def generate_ipv6(mac):
    parts = mac.split(":")
    parts.insert(3, 'ff')
    parts.insert(4, 'fe')
    parts[0] = format(int(parts[0], 16) ^ 0x02, '02x')  # Toggle bit 7
    ipv6 = "2001:db8::" + ":".join(["".join(parts[i:i+2]) for i in range(0, len(parts), 2)])
    return ipv6

def network_view(request):
    result = None
    if request.method == 'POST':
        form = NetworkForm(request.POST)
        if form.is_valid():
            mac = form.cleaned_data['mac_address']
            dhcp = form.cleaned_data['dhcp_version']
            lease_time = "3600 seconds"
            now = datetime.utcnow().isoformat() + "Z"

           
            if not len(mac.split(":")) == 6:
                result = "MAC inválida"
            else:
                if mac in leases:
                    assigned_ip = leases[mac]
                else:
                    if dhcp == 'DHCPv4':
                        assigned_ip = generate_ipv4(mac)
                    else:
                        assigned_ip = generate_ipv6(mac)
                    leases[mac] = assigned_ip

                data = {
                    "mac_address": mac,
                    "dhcp_version": dhcp,
                    "assigned_ip": assigned_ip,
                    "lease_time": lease_time,
                    "timestamp": now
                }
                collection.insert_one(data)
                result = data
    else:
        form = NetworkForm()

    return render(request, 'network/form.html', {'form': form, 'result': result})
