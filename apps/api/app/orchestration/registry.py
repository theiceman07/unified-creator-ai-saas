
import yaml

from app.capabilities._base import Capability


class Registry:
    def __init__(self):
        self.capabilities = {}
    
    def load(self, registry_path: str):
        with open(registry_path, 'r') as f:
            data = yaml.safe_load(f)
        for cap in data.get('orchestrators', []) + data.get('specialists', []):
            name = cap['name']
            self.capabilities[name] = {"config": cap, "class": None}

    def get_capability(self, name: str) -> Capability:
        if name not in self.capabilities:
            raise ValueError(f"Capability {name} not found in registry")
        cap_class = self.capabilities[name].get('class')
        if not cap_class:
            raise NotImplementedError(f"Capability {name} is defined in registry but not implemented yet")
        return cap_class()

registry = Registry()
# Assuming registry is loaded on app startup
