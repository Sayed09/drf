def mapping_value(e):
    if "view" in e:
        return "read"
    elif "add" in e:
        return "write"
    elif "change" in e:
        return "update"
    else:
        return "delete"