class Logger:
    _log_template = "{module}: {mess}"

    def __init__(self):
        pass

    def log(self, mod, mess):
        print(self._log_template.format(module=mod, mess=mess))
