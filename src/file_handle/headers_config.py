def get_volume_pattern(unit):
    if "bbl" in unit or "L" in unit:
        return r".*VOL.*|.*BARREL.*"
    else:
        return None
