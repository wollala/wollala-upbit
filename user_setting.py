import json
import os.path


class UserSetting:
    CONFIG_FILE = 'config.json'

    def __init__(self):
        self.upbit = {
            "access_key": "",
            "secret_key": "",
        }

        self.read_config_file()

    def write_config_file(self):
        with open(UserSetting.CONFIG_FILE, 'w') as _cfg_file:
            _cfg_json = {
                "upbit": self.upbit
            }
            json.dump(_cfg_json, _cfg_file, indent=2, ensure_ascii=False)

    def read_config_file(self):
        if not os.path.isfile(UserSetting.CONFIG_FILE):
            self.write_config_file()

        with open(UserSetting.CONFIG_FILE, 'r') as _cfg_file:
            _cfg_json = json.load(_cfg_file)
            self.upbit = _cfg_json['upbit']

