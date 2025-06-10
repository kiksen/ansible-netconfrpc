# ansible-netconfrpc

A collection of ansible roles for legacy netconf rfc calls used by Cisco IOS. Don't confuse it with the new netconf [RFC 6241](https://datatracker.ietf.org/doc/html/rfc6241) which obsoletes RFC 4741 and uses Yang models.

This is an older technology. Find some information [here on Ciscos website](https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/cns/configuration/15-s/cns-15-s-book/cns-netconf.html#GUID-4EFC48BB-C72F-4442-BAE4-0D0BFA1D3082 "Optionaler Linktitel") or check [RFC 4741](https://datatracker.ietf.org/doc/html/rfc4741).

The old version is bascially a cli wrapper which allows to send CLI configurations to your device. The advantages are no prompts (e.g. when deleting a user) and the configuration is transfered to the device before it is executed.


allowed configuration

block configuration


global configuration

working with interface configuration


vlan configuration
