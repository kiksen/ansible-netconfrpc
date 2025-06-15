# filter_plugins/interface_filters.py
import re


class FilterModule(object):
    def filters(self):
        return {
            'extract_vlans': extract_vlans,
            'find_vlans_to_change': find_vlans_to_change,
            'find_vlans_to_remove': find_vlans_to_remove,
            'find_vlans_to_remove_replace': find_vlans_to_remove_replace
        }


def expand_vlan_range(vlan_range):
    """
    Wandelt eine VLAN-Range-Zeichenkette wie '100,105-107' in eine Liste von VLAN-IDs als Strings um.
    """
    vlan_ids = []
    parts = vlan_range.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            vlan_ids.extend(str(vlan_id) for vlan_id in range(int(start), int(end) + 1))
        elif part.isdigit():
            vlan_ids.append(part.strip())
    return vlan_ids

def extract_vlans(config_lines):
    """ 
    VLAN Definition Extractor
    
    This function extracts VLAN definitions from a Cisco configuration file, processing it line by line. It returns a dictionary where the keys are VLAN IDs represented as strings.
    
    Supported features include:
    - Single VLAN definitions
    - VLAN ranges and lists (e.g., "vlan 100,200-202")
    - Optional VLAN names
    
    Function Parameters:
    - config_lines: A list of strings representing the Cisco configuration.        
    Return vlue:
    dict[str, dict]
        VLAN-ID (str) → {"name": <str>(optional) } 
    """
   
    vlan_data = {}
    current_vlans = []
    current_name = None

    # split config lines if they are not a list
    if type(config_lines) == str:
        config_lines = config_lines.split("\n")

    for line in config_lines:
        #stripped = line.strip()
        stripped = line

        if stripped.startswith("vlan "):
            vlan_part = stripped[5:]  # Alles nach "vlan "
            current_vlans = expand_vlan_range(vlan_part)
            current_name = None

        elif stripped.startswith(" name ") and current_vlans:
            current_name = stripped[6:]  # Alles nach "name "

        elif stripped == "!" and current_vlans:
            for vlan_id in current_vlans:
                entry = {}
                if current_name:
                    entry["name"] = current_name
                vlan_data[vlan_id] = entry
            current_vlans = []
            current_name = None

    return vlan_data


def find_vlans_to_change(current_vlans, vlans_toChange):
    """

    Parameter:
    ----------
    current_vlans -> dict:
        each vlan ID is a key (str) and has a dict like { 'name': 'Office' } as value.

    vlans_toChange -> list of dicts:
        each entry looks like: { 'vlan_id': 100, 'name': 'Office' }

    return value -> list of dicts:
        each entry looks like: { 'vlan_id': 100, 'name': 'Office' }
        It contains all vlans which are not present or the name needs to be changed.

    """
    missing = []

    for vlan in vlans_toChange:
        vlan['vlan_id'] = str( vlan['vlan_id'])
        vlan_id = vlan.get("vlan_id")
        name = vlan.get("name")

        # check if van_id exists
        if vlan_id not in current_vlans:
            missing.append(vlan)
            continue

        # check if the name is equal
        current_vlans_entry = current_vlans[vlan_id]
        current_vlans_name = current_vlans_entry.get("name")

        if current_vlans_name != name:
            missing.append(vlan)

    return missing


def find_vlans_to_remove(current_vlans, vlan_ids):
    """
    This function identifies the VLANs that still require deletion, ensuring that only existing VLANs are removed and preventing the deletion of non-existent VLANs.

    Parameter:
    ----------
    current_vlans -> dict:
        each vlan ID is a key (str) and has a dict like { 'name': 'Office' } as value.

    vlan_ids : list of str or int
        A list of integer or string values: [100, 200, 300]

    result : list
        A list of vlan_ids as integer [100, 200, 300]
    """
    existing = []

    for vlan_id in vlan_ids:
        if str(vlan_id) in current_vlans:
            existing.append(vlan_id)

    return existing


def find_vlans_to_remove_replace(current_vlans, vlans_toChange):
    """
    Calculates the difference between the current VLANs (dict) and the VLANs to be added.
    This yields the VLANs that are currently on the device but should no longer be present after the merge
    """
    add_vlan_ids = {str(vlan["vlan_id"]) for vlan in vlans_toChange}
    missing_ids = [vlan_id for vlan_id in current_vlans if vlan_id not in add_vlan_ids]
    return missing_ids

