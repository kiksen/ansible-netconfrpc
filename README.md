# ansible-netconfrpc

A collection of ansible roles for legacy netconf rfc calls used by Cisco IOS. Don't confuse it with the new netconf [RFC 6241](https://datatracker.ietf.org/doc/html/rfc6241) which obsoletes RFC 4741 and uses Yang models which is now used on IOS-XE devices.

This is an older technology. Find some information [here on Ciscos website](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/cns/configuration/15-s/cns-15-s-book/cns-netconf.html#GUID-4EFC48BB-C72F-4442-BAE4-0D0BFA1D3082 "Optionaler Linktitel") or check [RFC 4741](https://datatracker.ietf.org/doc/html/rfc4741).

The old version is bascially a cli wrapper which allows to send CLI configurations to your device. The advantages are no prompts (e.g. when deleting a user) and the configuration is transfered to the device before it is executed.

Available roles:
[get configuration](https://github.com/kiksen/ansible-netconfrfc/edit/main/README.md#get-configuration)


## Device configuration
You need a user which has priviledge level 15. SSH needs to be enabled. netconf is used via port 22 using 'netconf' subsystem.
```
conf t
username admin privilege 15 password test
netconf
```

# Roles

## get configuration

This role retrieves the complete device configuration. The result will be stored in the netconfrpc_result. Additionally, it is possible to specify a list of show commands to be retrieved in a single request from the device. The results of these commands will be stored in show_result.

### Options

#### `type`

- **Type**: String  
- **Required**: No  
- **Default**: `running`  
- **Choices**: `running`, `derived`, `startup`  
- **Description**: Specifies the type of configuration to retrieve.

#### `show_commands`

- **Type**: List of strings  
- **Required**: No  
- **Default**: `[]`  
- **Description**: A list of show commands to execute. Provide only the specific items you want to display, such as `'version'` or `'inventory'`.

#### `debug`

- **Type**: Boolean  
- **Required**: No  
- **Default**: `false`  
- **Description**: Enables debug output.
  
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

## allowed configuration

block configuration


global configuration

working with interface configuration


vlan configuration
