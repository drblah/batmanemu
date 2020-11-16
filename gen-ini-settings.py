import math
import argparse

def make_config(xsize, ysize, runTime):
    numHosts = xsize * ysize

    taps_and_namespaces = ""
    positions = ""

    for i in range(0, numHosts):
        taps_and_namespaces += '*.host[{}].wlan[0].device = "tap{}"\n'.format(i, i)
        taps_and_namespaces += '*.host[{}].wlan[0].namespace = "host{}"\n'.format(i, i)

    host_number = 0
    position_multiplyer = 100
    for y in range(0, ysize):
        for x in range(0, xsize):
            positions += '*.host[{}].mobility.initialX = {}m\n'.format(host_number, x*position_multiplyer)
            positions += '*.host[{}].mobility.initialY = {}m\n'.format(host_number, y*position_multiplyer)
            host_number = host_number + 1

    with open("template_omnetpp.ini", 'r') as template_file:
        template = template_file.read()
        with open("omnetpp_auto.ini", 'w') as output_file:
            template = template.format(runTime, numHosts, taps_and_namespaces, positions)
            output_file.write(template)

def main():
    parser = argparse.ArgumentParser(description='Generate ini config.')
    parser.add_argument('--xsize', action='store', type=int)
    parser.add_argument('--ysize', action='store', type=int)
    parser.add_argument('--run_time', action='store', type=str)

    arguments = parser.parse_args()

    make_config(arguments.xsize, arguments.ysize, arguments.run_time)



if __name__ == "__main__":
    main()