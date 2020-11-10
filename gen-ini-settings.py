numHosts = 64

for i in range(0, numHosts):
    print('*.host[{}].wlan[0].device = "tap{}"'.format(i, i))
    print('*.host[{}].wlan[0].namespace = "host{}"'.format(i, i))

host_number = 0
position_multiplyer = 100
for y in range(0, 8):
    for x in range(0, 8):
        print('*.host[{}].mobility.initialX = {}m'.format(host_number, x*position_multiplyer))
        print('*.host[{}].mobility.initialY = {}m'.format(host_number, y*position_multiplyer))
        host_number = host_number + 1