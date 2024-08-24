class AppInfo:
    def __init__(self, software_info, config):
        self.software_info = software_info
        self.config = config
        self.__name__ = dict.__name__

    def __call__(self):
        return {
            "name": "OpenServer",
            "developer": self.software_info.developer,
            "description": "Open-Source TheProtocols server",
            "icon": f"http{'' if self.config.Serve.Debug else 's'}://{self.config.Serve.Domain}/openserver/icon.png",
            "latest_build_number": self.software_info.build,
            "latest_version": self.software_info.version,
            "preferences": {}
        }
