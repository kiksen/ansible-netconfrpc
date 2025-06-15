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
    Extrahiert VLAN-Definitionen aus einer Cisco-Konfiguration (Zeile für Zeile).

    Gibt ein Dictionary zurück, in dem die Keys VLAN-IDs als Strings sind.

    Unterstützt:
    - Einzelne VLANs
    - Ranges und Listen (z. B. "vlan 100,200-202")
    - Optionale Namen

    Parameter:
    ----------
    config_lines : list of str
        Die Cisco-Konfiguration als Liste von Strings.

    Rückgabewert:
    -------------
    dict[str, dict]
        VLAN-ID (als String) → {"name": <str>} falls vorhanden, sonst leeres Dict.
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
    Mit der Funktion wird geguckt welche Vlans noch angelegt oder verändert werden müssen.

    Prüft, welche VLAN-IDs aus einer gegebenen Liste im result-Dictionary vorhanden sind.

    Diese Funktion durchsucht die übergebene Liste von VLAN-IDs und prüft,
    ob jede dieser IDs als Key im result-Dictionary existiert.
    Es wird nur die Existenz der VLAN-ID überprüft – der VLAN-Name wird ignoriert.

    Parameter:
    ----------
    vlan_ids : list of str
        Eine Liste von VLAN-IDs, die überprüft werden sollen (z.B. ['100', '200']).

    result : dict
        Ein Dictionary, das VLAN-IDs als Keys enthält.
        Die Werte können z. B. {'name': 'some_name'} sein oder leer.

    Rückgabewert:
    -------------
    list of str
        Eine Liste von VLAN-IDs, die im result-Dictionary vorhanden sind.
    """
    missing = []

    for vlan in vlans_toChange:
        vlan['vlan_id'] = str( vlan['vlan_id'])
        vlan_id = vlan.get("vlan_id")
        name = vlan.get("name")

        # Prüfen, ob die VLAN-ID existiert
        if vlan_id not in current_vlans:
            missing.append(vlan)
            continue

        # Prüfen, ob der Name übereinstimmt
        current_vlans_entry = current_vlans[vlan_id]
        current_vlans_name = current_vlans_entry.get("name")

        if current_vlans_name != name:
            missing.append(vlan)

    return missing


def find_vlans_to_remove(current_vlans, vlan_ids):
    """
    Diese funktion wird dazu verwendet um zu gucken welche Vlans noch gelöscht werden müssen
    damit keine Vlans gelöscht werden die nicht existieren

    Prüft, welche VLAN-IDs aus der liste vlans_ids im current_vlans dictionaray nicht als key vorhanden sind.

    Parameter:
    ----------
    vlan_ids : list of str or int
        Eine Liste von VLAN-IDs als Integer oder String

    result : list
        Eine Liste mit vlan IDs als integer
    Rückgabewert:
    -------------
    list of str
        Eine Liste von VLAN-IDs, die im result-Dictionary vorhanden sind.
    """
    existing = []

    for vlan_id in vlan_ids:
        if str(vlan_id) in current_vlans:
            existing.append(vlan_id)

    return existing


def find_vlans_to_remove_replace(current_vlans, vlans_toChange):
    """
    Erzeugt die Differenz zwischen current_Vlans (dict) und den Vlans die hinzugefügt werden sollen.
    Damit erhält man die Vlans die noch auf dem Device sind, die aber nach dem Merge nicht mehr da sein sollen.
    """
    add_vlan_ids = {str(vlan["vlan_id"]) for vlan in vlans_toChange}
    missing_ids = [vlan_id for vlan_id in current_vlans if vlan_id not in add_vlan_ids]
    return missing_ids

