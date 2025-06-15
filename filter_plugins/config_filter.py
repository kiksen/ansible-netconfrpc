# filter_plugins/interface_filters.py
import re


class FilterModule(object):
    def filters(self):
        return {
            'extract_interfaces': extract_interfaces,
            'extract_block': extract_block
        }


def extract_interfaces(config_content):
    """
    Gets a Cisco configuration file (as string with \n after each line or as list) and returns all interfaces and their configuration as dictionary.
    Each interface name like GigabitEthernet3 is a key and all configuration lines will be returned as value.
    """
    interfaces = {}
    current_interface = None

    if isinstance(config_content, str):
        config_lines = config_content.splitlines()
    else:
        config_lines = config_content

    for line in config_lines:
        if line.lstrip().startswith("interface"):
            current_interface = line.strip().split()[1]
            interfaces[current_interface] = []
        elif current_interface:
            if line.startswith(" ") or line.startswith("\t"):
                interfaces[current_interface].append(line.strip())
            elif line.strip() == "!":
                current_interface = None

    return interfaces


def extract_block(config_content, startblock, endblock):
    """
    Extracts a block conf configuration from config_content.
    startblock defines the start of the block
    endblock defines the end of the block
    The block is returned as list.
    """
    block = []
    blockstarted = False

    if isinstance(config_content, str):
        config_lines = config_content.splitlines()
    else:
        config_lines = config_content

    for line in config_lines:

        if line.strip() == startblock:
            blockstarted = True
        elif line.strip() == endblock and blockstarted:
            blockstarted = False
            break
        elif blockstarted:
            block.append( line.strip())

    return block

