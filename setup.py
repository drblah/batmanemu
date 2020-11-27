import os
import argparse
import string
import subprocess

from pyroute2 import NetNS, netns


def create_namespace(id):
    result = os.system("ip netns add host{}".format(id))

    if result != 0:
        print("Failed to create namespace for id: {}. Aborting!".format(id))
        exit()


def create_TAP(id):
    result = os.system("ip netns exec host{} ip tuntap add mode tap dev tap{}".format(id, id))

    if result != 0:
        print("Failed to create TAP for id: {}. Aborting!".format(id))
        exit()

    result = os.system("ip netns exec host{} ip link set dev tap{} mtu 1560".format(id, id))

    if result != 0:
        print("Failed to set mtu for id: {}. Aborting!".format(id))
        exit()

    result = os.system("ip netns exec host{} ip link set dev tap{} up".format(id, id))

    if result != 0:
        print("Failed to UP TAP for id: {}. Aborting!".format(id))
        exit()


def create_batman_interface(id):
    result = os.system("ip netns exec host{} batctl if add tap{}".format(id, id))

    if result != 0:
        print("Failed to create BAT interface for id: {}. Aborting!".format(id))
        exit()

    result = os.system("ip netns exec host{} ip link set dev bat0 up".format(id))

    if result != 0:
        print("Failed to UP BAT interface for id: {}. Aborting!".format(id))
        exit()

    result = os.system("ip netns exec host{} ip addr add 192.168.2.{}/24 dev bat0".format(id, id+1))

    if result != 0:
        print("Failed to assign IP to interface for id: {}. Aborting!".format(id))
        exit()


def set_hop_penalty(id, penalty):
    result = os.system("ip netns exec host{} batctl meshif bat0 hop_penalty {}".format(id, penalty))

    if result !=0:
        print("Failed to set hop penalty for id: {}. Aborting!".format(id))
        exit()

def set_ogm_interval(id, interval):
    result = os.system("ip netns exec host{} batctl meshif bat0 orig_interval {}".format(id, interval))

    if result !=0:
        print("Failed to set ogm interval for id: {}. Aborting!".format(id))
        exit()


def extract_attr_value(if_attrs, keyname):
    for attr in if_attrs:
        if attr[0] == keyname:
            return attr[1]

def get_mac_addr(host, dev):

    with NetNS(host) as ns:
        links = ns.get_links()

        for l in links:
            # If the device name matches the one we are looking for
            if extract_attr_value(l['attrs'], 'IFLA_IFNAME') == dev:
                # return the mac address
                return extract_attr_value(l['attrs'], 'IFLA_ADDRESS')


def get_ip_addr(host, dev):

    with NetNS(host) as ns:
        addrs = ns.get_addr()

        for addr in addrs:
            # If the device name matches the one we are looking for
            if extract_attr_value(addr['attrs'], 'IFA_LABEL') == dev:
                # return the IP address
                return extract_attr_value(addr['attrs'], 'IFA_ADDRESS')

def create_static_arp():
    arp_table = []

    # Populate our static arp table
    for ns in netns.listnetns():
        arp_table.append({ "host": ns,
                          "mac": get_mac_addr(ns, 'bat0'),
                          "ip": get_ip_addr(ns, 'bat0') })

    # Assign it to all hosts. Skip self.
    for ns in netns.listnetns():
        for arp in arp_table:
            if arp["host"] != ns:
                os.system("ip netns exec {} arp -s {} {}".format( ns, arp['ip'], arp['mac'] ))



def cleanup():
    stream = os.popen('ip netns')

    hosts = stream.readlines()

    print("Host to be cleaned up:")
    for h in hosts:
        print(h.strip())
    
    for h in hosts:
        id = int(h.strip(string.ascii_letters))
        
        # destroy TAP interfaces
        result = os.system("ip netns exec host{} ip tuntap del mode tap dev tap{}".format(id, id))

        if result != 0:
            print("Failed to remove TAP interface for id: {}".format(id))
            exit()

        # destroy network namespaces
        result = os.system("ip netns del host{}".format(id))

        if result != 0:
            print("Failed to remove namespace for id: {}".format(id))
            exit()


def main():
    parser = argparse.ArgumentParser(description='Configure namespace hosts for simulation.')
    parser.add_argument('--cleanup', action='store_true', default=False)
    parser.add_argument('--nhosts', action='store', type=int)
    parser.add_argument('--batv', action='store_true', default=False)
    parser.add_argument('--hop_penalty', action='store', type=int)
    parser.add_argument('--ogm_interval', action='store', type=int)
    parser.add_argument('--static_arp', action='store_true', default=False)

    arguments = parser.parse_args()

    if arguments.cleanup:
        print("Cleaning up...")
        cleanup()

        print("\n-----\nDone!")
    else:

        os.system("modprobe batman-adv")

        if arguments.batv:
            os.system("batctl ra BATMAN_V")
        else:
            os.system("batctl ra BATMAN_IV")

        for i in range(0, arguments.nhosts):
            create_namespace(i)
            create_TAP(i)
            create_batman_interface(i)

            if arguments.hop_penalty:
                set_hop_penalty(i, arguments.hop_penalty)
            if arguments.ogm_interval:
                set_ogm_interval(i, arguments.ogm_interval)

        if arguments.static_arp:
            create_static_arp()

if __name__ == "__main__":
    main()