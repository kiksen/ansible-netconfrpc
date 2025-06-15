# ansible-netconfrpc

A collection of ansible roles for legacy netconf rfc calls used by Cisco IOS. Don't confuse it with the new netconf [RFC 6241](https://datatracker.ietf.org/doc/html/rfc6241) which obsoletes RFC 4741 and uses Yang models which is now used on IOS-XE devices.

This is an older technology. Find some information [here on Ciscos website](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/cns/configuration/15-s/cns-15-s-book/cns-netconf.html#GUID-4EFC48BB-C72F-4442-BAE4-0D0BFA1D3082 "Optionaler Linktitel") or check [RFC 4741](https://datatracker.ietf.org/doc/html/rfc4741).

The old version is basically a cli wrapper which allows to send CLI configurations to your device. The advantages are no prompts (e.g. when deleting a user) and the configuration is transfered to the device before it is executed.

Available roles:
- [get configuration](https://github.com/kiksen/ansible-netconfrfc/blob/main/README.md#get-configuration)
- [allowed configuration](https://github.com/kiksen/ansible-netconfrfc/blob/main/README.md#allowed-configuration)
- [block configuration](https://github.com/kiksen/ansible-netconfrfc/blob/main/README.md#blockconfig)
- [global configuration](https://github.com/kiksen/ansible-netconfrfc?tab=readme-ov-file#globalconfig)
- [interfaces](https://github.com/kiksen/ansible-netconfrfc/blob/main/README.md#interface)
- [vlans](https://github.com/kiksen/ansible-netconfrfc/blob/main/README.md#vlan-configuration)

## Device configuration
A priviledge level 15 user is needed abd SSH needs to be enabled. netconf is used via port 22 using 'netconf' subsystem.
```
conf t
username admin privilege 15 password test
netconf
```

## General Notes:
- The ansible.netcommon.netconf_rpc calls always report a "changed" state. If no changes are made, the task will be marked as skipped.
- All roles provide a debug option that enables detailed output for troubleshooting purposes."

## Directory Structure

* ....\ANSIBLE\ANSIBLE-NETCONFRFC
  * filter_plugins
  * roles
    * netconfrpc
      * allowedConfig
        * handlers
        * meta
        * tasks
        * vars
      * blockConfig
        * handlers
        * meta
        * tasks
        * vars
      * getConfiguration
        * meta
        * tasks
        * vars
      * globalConfig
        * handlers
        * meta
        * tasks
        * vars
      * interface
        * handlers
        * meta
        * tasks
        * vars
      * saveConfig
        * meta
        * tasks
      * vlans
        * handlers
        * meta
        * tasks
        * vars

## Handlers
If a role does a change a handler named "Write running config" will be notified. Each role has a handlers file which safes the running configuration.

# Roles

## get configuration

This role retrieves the complete device configuration. The result will be stored in the netconfrpc_result. Additionally, it is possible to specify a list of show commands to be retrieved in a single request from the device. The results of these commands will be stored in show_result.

### Example
```
    - name: Get Config from device
      vars:
        show_commands: <- show commands are optional
          - version
          - inventory
      include_role:
        name: netconfrpc/getConfiguration
```

### Options
#### `type:`
- **Required**: No  
- **Choices**: `running` (default), `derived`, `startup`  
- **Description**: Specifies the type of configuration to retrieve.

#### `show_commands:`

- **Type**: List of strings  
- **Required**: No  
- **Default**: `[]`  
- **Description**: A list of show commands to execute. Provide only the specific items you want to display, such as `'version'` or `'inventory'`.

#### `debug:`

- **Type**: Boolean  
- **Required**: No  
- **Default**: `false`  
- **Description**: Enables debug output.

#### `Results:`
getConfiguration will return 'netconfrpc_result' which has the following fields:

| Key         | value                                                   |
|----------------|---------------------------------------------------------------|
| stdout  | The current config from the device as string. Like ansible_net_config from ios_facts |
| stdout_lines | The current config as a list of strings (used by all filter for theses roles)  |
| show_result | Dictinary containing all show commands e.g. 'version' as key and the output as value |
| interfaces | Dictionary containing the interface name as key and all configuration lines as value |
| vlans | Dictionarry containing each vlan_id as key and the name as value  |




## allowed configuration

### Description
This role removes unwanted configuration elements such as users, NTP servers, or RADIUS configurations.

A regular expression (regex pattern) is used to extract the relevant part of each configuration line to generate a corresponding `no` command for removal.  
The regex must contain exactly **one capturing group** `()` which will be used to build the command.  
For example:  
- Configuration line: `username Cisco`  
- Regex pattern: `^(username \w+).*$`  
- Resulting command: `no username Cisco`  

**Important:** The regex must match the entire line.

### Example
The following playbook will delete Legacy_Unix1 and Legacy_Unix2 and keep ISE1 and ISE2.
```
  # A device has the following configuration:
  # radius server ISE1
  #  address ipv4 10.1.1.1 auth-port 1812 acct-port 1813
  # radius server ISE2
  #  address ipv4 20.1.1.1 auth-port 1812 acct-port 1813
  # radius server Legacy_Unix1
  #  address ipv4 30.1.1.1 auth-port 1812 acct-port 1813
  # radius server Legacy_Unix2
  #  address ipv4 40.1.1.1 auth-port 1812 acct-port 1813

    - name: Make sure only our allowed radius server are configured!
      vars:
        allowed:
          - radius server ISE1
          - radius server ISE2
        pattern: '^(radius server \w+)$'
        current_config: "{{ full_config }}"
        debug: true
      include_role:
        name: netconfrpc/allowedConfig
```

These example shows how to remove all snmpv2 configurations from a device to ensure we don't have any legacy configurations.
```
    - name: Remove all snmp v2 configurations
      vars:
        pattern: '^(snmp-server community \w+).*$'
        current_config: "{{ full_config }}"
        debug: true
      include_role:
        name: netconfrpc/allowedConfig
```

### Options
#### `pattern`:
- **Type**: String  
- **Required**: Yes  
- **Description**:  
  A regex pattern used to extract the relevant configuration lines for removal. The pattern must contain exactly one capturing group.

#### `allowed:`
- **Type**: List of strings  
- **Required**: No  
- **Description**:  
  A list of allowed configuration entries. These must exactly match the captured group from the pattern (e.g., `username Cisco`).
  If you don't use allowed, all found lines will be removed. See examples.

#### `current_config:`
- **Type**: List of strings  
- **Required**: Yes  
- **Description**:  
  The current full device configuration as a list of strings.

#### `debug:`
- **Type**: Boolean  
- **Required**: No  
- **Description**:  
  Enables debug output for troubleshooting.


# blockConfig

**Description**  
This role makes sure all lines from a block of configuration is present or removed. This role can be used for access lists or any other block of configuration lines. It doesn't need to be an indented block of config like access-lists or class-maps.

### Example
The following example will create an access-list MGMT. If the list exists and if lines are different it will be removed by 'before' command and recreated.
Since the configuration will be not send line by line but as a block via netconf you can use it to modify the access list on line configurations.
```
    - name: Re-create access list
      vars:
        start_block: ip access-list standard MGMT
        end_block: '!'
        before: no ip access-list standard MGMT
        intended_config:
          - 10 permit 10.1.1.0 0.0.0.255
          - 20 permit 20.1.1.1
          - 40 remark Managment network
          - 50 permit 30.1.1.0 0.0.0.255
        current_config: "{{ full_config }}"
        debug: true
      include_role:
        name: netconfrpc/blockConfig
```

The following example starts with a routemap like this. 
```
route-map TEST permit 10
  match ip address 102
  set tag 123
```

You want to replace 102 by 101. If you don't use default_config you will end up with "match ip address 101 102".
```
    - name: Route-map
      vars:
        start_block: route-map TEST permit 10
        end_block: '!'
        intended_config:
          - match ip address 102
          - set tag 123
        default_config:
          - no match ip address 101
        current_config: "{{ full_config }}"
        debug: false
      include_role:
        name: netconfrpc/blockConfig
```

## Optionen
#### `start_block:`
- **Required:** Yes 
- **Description:**
  A line of configuration to start a config block: `ip access-list standard MGMT`

#### `end_block:`
- **Required:** Yes  
- **Description:**
  A line of configuration to end a config block: `!`

#### `before:`
- **Typ:** list (str)  
- **Required:** No  
- **Description:**  
  Commands you need to fix things up like deleting an access-list completely

#### `default_config:`
- **Typ:** list (str)  
- **Required:** No  
- **Description:**  
  A list of commands which are not visible in the final configuration

#### `current_config:`
- **Typ:** list (str)  
- **Required:** Yes
- **Description:**  
  Your current complete device config as list of strings.

# globalConfig
**Description**
Send global config commands to the device.

## Example
The following example sends two lines of configuration to the device. If they are found nothing is changed or done.
```
    - name: Send configuration lines to device
      vars:
        intended_config:
          - snmp-server community insecure RO
          - hostname netconfIsCoolxxx
        current_config: "{{ full_config }}"
        debug: true
      include_role:
        name: netconfrpc/globalConfig
```

## Options
### `before:`
- **Type:** list
- **Elements:** str
- **Required:** false
- **Description:** A list of commands which are sent to the device, but not used for checks if intended_config is reached.

### `intended_config:`
- **Type:** list
- **Elements:** str
- **Required:** false
- **Description:** A list of commands which are sent to the device. If a command of the list is missing, the config will be sent.

### `default_config:`
- **Type:** list
- **Elements:** str
- **Required:** false
- **Description:** A list of commands which are not visible in the final configuration. You can use this list for default commands or to remove things.

### `current_config:`
- **Type:** list
- **Elements:** str
- **Required:** true
- **Description:** Your current complete device config as string, which is used to determine the intended configuration.

### `unwanted_config:`
- **Type:** list
- **Elements:** str
- **Required:** true
- **Description:** If unwanted_config is found in the current_config, the execution is triggered.

### `debug:`
- **Type:** bool
- **Required:** false
- **Default:** false
- **Description:** Print more information when executing.

# interface

## Description
This role is used to manage and apply interface-level configurations on network devices. It can analyze current configurations, identify required changes, and apply the desired configuration state reliably.

## Example
```
    - name: Get Device configuration including interfaces and vlans
      include_role:
        name: netconfrpc/getConfiguration
    # will return netconffpc_result

    - name: Set Interface Configuration to Trunk
      vars:
        default_interface: true
        name: GigabitEthernet4
        current_config: "{{ netconfrpc_result.interfaces[name] }}"        
        intended_config:
        - description Switch1-to-Switch2
        - switchport mode trunk
        - switchport trunk allowed vlan 55,100,200,300
        - negotiation auto
        default_config:
          - switchport trunk native vlan 1
          - logging event link-status
          - mop enabled
          - mop sysid
        debug: true
      include_role:
        name: netconfrpc/interface
```

## Options
### `name:`
- **Type**: `str`
- **Required**: Yes  
- **Description**: Interface name, e.g., `GigabitEthernet1/0/1`.

### `current_config:`
- **Type**: `list` (elements of type `str`)  
- **Required**: Yes
- **Description**:  
  A list of all configuration lines currently found on the interface. These can be obtained using the `getConfiguration` role, which returns `netconfrpc.interfaces[name]`. These are only the config lines without "interface GigabitEthernetxxx".

### `intended_config:`
- **Type**: `list` (elements of type `str`)  
- **Required**: Yes  
- **Description**:  
  A list of configuration commands to be sent to the device.

### `default_interface:`
- **Type**: `bool`  
- **Required**: No  
- **Default**: `false`  
- **Description**:  
  Sends `default interface <name>` before pushing configuration to the device.

### `default_config:`
- **Type**: `list` (elements of type `str`)  
- **Required**: No  
- **Description**:  
  Lines that are not visible after being sent to the configuration. These are usually default commands like `logging event link-status`.  
  If you don't want logging, you need to add `no logging event link-status` to `target_config`, since you will see it in the running configuration.

# vlan configuration
## Description
This Ansible module allows you to write or remove VLANs from your device..

## Example
The following example will add vlan 100,200, 555 and 888. Exisitng vlans will remain unchached. 200 and 1000 will be removed.
```
    - name: Get running configuration
      include_role:
        name: netconfrpc/getConfiguration

    - name: Change vlans
      vars:
        current_configuration: "{{ netconfrpc_result.stdout_lines }}"
        debug: true
        add_vlans:
          - vlan_id: 100
            name: Office
          - vlan_id: 200
            name: Data
          - vlan_id: 555
            name: Management
          - vlan_id: 888
            name: secret
        remove_vlans:
          - 200
          - 1000
      include_role:
        name: netconfrpc/vlans
```

This example will add vlan 100, 200, 555 and 888 and remove all other vlans which are found on the device (except vlan1).
```
    - name: Get running configuration
      include_role:
        name: netconfrpc/getConfiguration

    - name: Change vlans
      vars:
        current_configuration: "{{ netconfrpc_result.stdout_lines }}"
        debug: true
        add_vlans:
          - vlan_id: 100
            name: Office
          - vlan_id: 200
            name: Data
          - vlan_id: 555
            name: Management
          - vlan_id: 888
            name: secret
        replace: true
      include_role:
        name: netconfrpc/vlans
```

## Options
### `current_config:`
- **Type**: string  
- **Required**: No  
- **Description**:  
  Complete device configuration including all VLANs.

### `add_vlans:`
- **Type**: list  
- **Required**: No  
- **Description**:  
  A list of VLANs to add.  
  Example:
  ```yaml
  add_vlans:
    - vlan_id: 123
      name: Test
  ```

### `replace:`
- **Type**: boolean  
- **Required**: No  
- **Default**: false  
- **Description**:  
  Use only if set to true. If replace is defined remove_vlans is not used, only 'add_vlans' will remain on the device, all other vlans found will be removed.
  
### `remove_vlans:`
- **Type**: list of integers  
- **Required**: No  
- **Default**: false  
- **Description**:  
  A list of VLAN IDs to remove.  
  Example:
  ```yaml
  remove_vlans:
    - 123
    - 200
    - ...
  ```

### `debug:`
- **Type**: boolean  
- **Required**: No  
- **Default**: false  
- **Description**:  
  Print more information when executing.
