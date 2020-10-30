# batmanemu
Batman-adv emulation using OMNET++, inet and Linux network namespaces

## Usage
1. Clone into inet/examples/adhoc/batmanemu
2. Run setup.py as sudo with the desired parameters.
```
sudo python3 setup.py --nhosts 10
```
This will create 10 namespaces each with a TAP device. Each tap device is added as a Batman-adv device and assigned an IP address. **NOTE:** at this time, the batman interfaces are assigned IPv4/24 so it can only do up to 254 hosts. This is because the address are assigned using a call to IP using string interpolation.
3. Set the necessary capabilities on your OMNET++ executable so it can interact with the namespaces and TAP devices.
```
sudo setcap cap_sys_admin+ep opp_run
```
Where opp_run is located in ${OMNET_HOME}/bin.

4. Run the simulation in release mode. If you are using Qtenv, make sure to run in "express" mode.
