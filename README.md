# ospf-frr-security
Virtual Lab using VNX( Virtual Networks over linuX)  to test the security of OSPFv2 and OSPFv3

## Topology overview:
![Topology](img/OSPF_Topology.png)

## Topology in detail:
![Topology](img/Topologia.png)


## Scenario preparation


It is necessary to download the file system image used by the scenario instances. From the directory `OSPF_FRR/filesystems`, execute:


```bash
sudo vnx_download_rootfs -r vnx_rootfs_lxc_ubuntu64-22.04-v025-fw.tgz
sudo ln -s vnx_rootfs_lxc_ubuntu64-22.04-v025-fw rootfs_lxc
```
### Hosts and routers credentials:

Username:root
Password:xxxx

# Test scenario OSPF-FRR 

OSPF with two areas, an area 0 (backbone) with 3 routers interconnected with point to point links.
And another area (area 1) with routers connected with point to multipoint links.

Both have ipv4 and ipv6 configured.

## Two Scenarios:

Scenario without security in the areas of OSPF:


```bash
sudo vnx -f frr-ospf-lan.xml -x loadra
sudo vnx -f frr-ospf-lan.xml -x loadrb
sudo vnx -f frr-ospf-lan.xml -x loadrc
sudo vnx -f frr-ospf-lan.xml -x loadrd
sudo vnx -f frr-ospf-lan.xml -x loadre
```
-----------------------------------------------------------------------------------------------------------
Scenario with security (OSPF trailer):

Command to load all configurations in the corresponding routers:

```bash
sudo vnx -f frr-ospf-lan.xml -x load_keys
```
Or it can be executed one by one:
```bash
sudo vnx -f frr-ospf-lan.xml -x loadra_key
sudo vnx -f frr-ospf-lan.xml -x loadrb_key
sudo vnx -f frr-ospf-lan.xml -x loadrc_key
sudo vnx -f frr-ospf-lan.xml -x loadrd_key
sudo vnx -f frr-ospf-lan.xml -x loadre_key
```

-----------------------------------------------------------------------------------------------------------
BY DEFAULT LOADS THE SCENARIO WITHOUT AUTHENTICATION IN OSPF.

FRR does not allow the use of IPSEC in OSPF, it is not possible to configure the command directly in the console.


-----------------------------------------------------------------------------------------------------------

## IP Addresses:
Hosts:
| Host      | Interfaz     | IPv4           | IPv6                                   |
|-----------|--------------|----------------|----------------------------------------|
| rA        | netA         | 10.7.1.1/28    | fd80:e42c:3ce3:a66a::1/64              |
| rA        | netA-B       | 10.8.1.1/30    | fd80:e42c:3ce3:a770::1/64              |
| rA        | netA-C       | 10.8.1.5/30    | fd80:e42c:3ce3:a770::2/64              |
| hA        | -            | 10.7.1.10/28   | fd80:e42c:3ce3:a66a::10/64             |
| rB        | netB         | 10.8.1.13/30   | fd80:e42c:3ce3:a66b::1/64              |
| rB        | netA-B       | 10.8.1.2/30    | fd80:e42c:3ce3:a770::3/64              |
| rB        | netB-C       | 10.8.1.9/30    | fd80:e42c:3ce3:a770::4/64              |
| hB        | -            | 10.8.1.14/30   | fd80:e42c:3ce3:a66b::10/64             |
| rC        | netC         | 10.8.1.17/30   | fd80:e42c:3ce3:a66c::1/64              |
| rC        | netA-C       | 10.8.1.6/30    | fd80:e42c:3ce3:a770::5/64              |
| rC        | netB-C       | 10.8.1.10/30   | fd80:e42c:3ce3:a770::6/64              |
| hC        | -            | 10.8.1.18/30   | fd80:e42c:3ce3:a66c::10/64             |
| rD        | netD         | 10.7.1.17/30   | fd80:e42c:3ce3:a66d::1/64              |
| rD        | netA         | 10.7.1.2/28    | fd80:e42c:3ce3:a66a::2/64              |
| hD        | -            | 10.7.1.18/30   | fd80:e42c:3ce3:a66d::10/64             |
| rE        | netE         | 10.7.1.21/30   | fd80:e42c:3ce3:a66e::1/64              |
| rE        | netA         | 10.7.1.3/28    | fd80:e42c:3ce3:a66a::3/64              |
| hE        | -            | 10.7.1.22/30   | fd80:e42c:3ce3:a66e::10/64             |


## OSPF trailer key changes 

The change.key script allows to automate the change of keys in the OSPF process.

Its main objective is to modify the key_id of the current keychain to add a maximum usage time and create a new key within the same key_chain to replace the old one.


The key change logic is as follows

### Current Key (`key_id`)

| Type             | From        | To          |
|------------------|-------------|-------------|
| accept lifetime  | date-time   | date-time   |
| send lifetime    | date-time   | date-time   |

### New Key (`key_id + 1`)

| Type             | From        | To        |
|------------------|-------------|-----------|
| accept lifetime  | date        | infinite  |
| send lifetime    | date        | infinite  |


## Python script to automate key changes 

The above logic is implemented in a python script in the /change_key directory
Use the following command to execute it:

```bash
sudo python3 change_key.py --key [Name of the Key-chain, Key_id in use, New_Password] --routername [name of the routers] --time {seconds}
```
### Key tag:

Defines the name of the key_chain in use, the key_id being used and the new key to be used together with the hmac-sha-256 algorithm for the OSPF trailer..

### Routername tag

Defines the set of routers that will be affected by this change.

-all (Changes all the routers of the scenario ["rA","rB","rC","rD","rE"])

### Time tag:

Defines the number of seconds to be used as interval, the minimum time is 60 seconds, if you enter a time less than 60 seconds, 60 seconds will be used.

### Examples:

```bash
sudo python3 change_key.py --key 1 1 EVANGELION --routername all --time 10
sudo python3 change_key.py --key 1 4 EVANGELION3 --routername rA rB --time 100
```

Commands to check that the keys have been changed:

```bash
show ip ospf interface {interface_name}
show running-config
```