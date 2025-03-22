class Settings:
    settings: dict = {}
    @classmethod
    def _SaveIniFile(cls, filename, dictionary):
        with open(filename, "w") as f:
            for key in dictionary:
                f.write("{},{}\n".format(key, dictionary[key]))
    
    @classmethod
    def _LoadIniFile(cls, filename):
        dictionary = {}
        with open(filename, "r") as f:
            for s in f:
                lst = s.strip().split(",")
                dictionary[lst[0]] = lst[1]
        return dictionary

    @classmethod
    def LoadSettings(cls):
        try:
            cls.settings = cls._LoadIniFile("/settings.ini")
            print("kbd_intr" in Settings.settings)
        except:
            pass
    
    @classmethod
    def SaveSettings(cls):
        print("saving settings")
        cls._SaveIniFile("/settings.ini", cls.settings)


