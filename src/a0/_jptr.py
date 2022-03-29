def _jptr_parse(ptr):
    if ptr == "":
        return []
    if ptr[0] != "/":
        raise ValueError("JSON Pointer must begin with '/'")
    return [part.replace("~0", "~").replace("~1", "/") for part in ptr[1:].split("/")]


def jptr_get(obj, ptr):
    parts = _jptr_parse(ptr)
    for part in parts:
        if type(obj) == list:
            if part == "-":
                part = -1
            else:
                part = int(part)
        obj = obj[part]
    return obj


def jptr_set(obj, ptr, val):
    parts = _jptr_parse(ptr)

    if not parts:
        raise ValueError("JSON Pointer cannot set root object")

    def handle_part(obj, part, default_subobj):
        is_list_idx = part == "-" or part.isdigit()

        if type(obj) == list:
            if not is_list_idx:
                raise ValueError("JSON Array cannot be indexed by a string")

            if part == "-":
                obj.append(default_subobj)
                return -1

            part = int(part)
            if len(obj) <= part:
                obj += [None] * (part - len(obj))
                obj.append(default_subobj)
            return part
        elif is_list_idx:
            raise ValueError("JSON Object cannot be indexed by a number")

        if len(part) > 1 and part[0] == part[-1] == '"':
            part = part[1:-1]

        if part not in obj:
            obj[part] = default_subobj
        return part

    for i, part in enumerate(parts[:-1]):
        next_part = parts[i + 1]
        default_subobj = [] if next_part == "-" or next_part.isdigit() else {}

        part = handle_part(obj, part, default_subobj)
        obj = obj[part]

    part = handle_part(obj, parts[-1], None)
    obj[part] = val
