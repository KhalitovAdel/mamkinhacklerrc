import os
import yaml

class ConfigProvider:
    def __init__(self, config_file_name=".mamkinhacklerrc"):
        self.__config_file_path = os.path.join(os.path.expanduser('~'), config_file_name)
        try:
            self.config_data = self.__load_config()
        except FileNotFoundError:
            self.config_data = {}

    # key format some.key.value
    # same key ENV format SOME_KEY_VALUE
    def get_property(self, key, default = None):
        envKey = ConfigProvider.__format_to_env_key(key)
        value = os.getenv(envKey)

        if value: 
            return value
        
        return self.config_data.get(key, default)
    
    def get_required_property(self, key: str) -> str:
        value = self.get_property(key)
        if not value:
            raise Exception(f"Property {key} not defined!")
        
        return value

    def __load_config(self):
        # ONLY YAML
        config_data = {}
        if os.path.exists(self.__config_file_path):
            with open(self.__config_file_path, 'r') as file:
                config_data = yaml.safe_load(file) or {} 

        return ConfigProvider.__flatten_dict(config_data)
    
    @staticmethod
    def __format_to_env_key(key: str) -> str:
        return key.replace('.', '_').upper()

    @staticmethod
    def __flatten_dict(d, parent_key='', sep='.'):
        items = {}
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(ConfigProvider.__flatten_dict(v, new_key, sep=sep))
            else:
                items[new_key] = v
        return items