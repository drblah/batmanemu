import os
import argparse
import string


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
    result = os.system("sudo ip netns exec host{} batctl if add tap{}".format(id, id))

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


if __name__ == "__main__":
    main()