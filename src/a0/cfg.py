from alephzero_bindings import *
from a0._jptr import *
import json


class cfg:
    def __init__(self, topic, jptr=None, type=None):
        self._cfg = Cfg(topic)
        self._jptr = jptr or ""
        self._type = type

    def _extract(self, pkt):
        cfg_val = json.loads(pkt.payload.decode())
        cfg_val = jptr_get(cfg_val, self._jptr)

        if not self._type:
            return cfg_val
        elif type(cfg_val) == dict:
            return self._type(**cfg_val)
        elif type(cfg_val) == list:
            return cfg_val if self._type == list else self._type(*cfg_val)

        return self._type(cfg_val)

    def read(self):
        return self._extract(self._cfg.read())

    def read_blocking(self, timeout=None):
        if timeout != None:
            return self._extract(self._cfg.read_blocking(timeout))
        else:
            return self._extract(self._cfg.read_blocking())

    def write(self, val, encoder=None):
        class ToJsonEncoder(json.JSONEncoder):
            def default(self, obj):
                if hasattr(obj, "tojson"):
                    return obj.tojson()

                return json.JSONEncoder.default(self, obj)

        encoded_val = (
            encoder(val) if encoder else json.loads(ToJsonEncoder().encode(val))
        )

        mergepatch = {}
        jptr_set(mergepatch, self._jptr, encoded_val)
        self._cfg.mergepatch(mergepatch)
