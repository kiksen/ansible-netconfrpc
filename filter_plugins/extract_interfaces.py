# filter_plugins/interface_filters.py



class FilterModule(object):
    def filters(self):
        return {
            'extract_interfaces': extract_interfaces
        }


def extract_interfaces(config_content):
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