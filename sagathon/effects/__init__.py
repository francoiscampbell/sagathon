from __future__ import print_function


class Effect(object):
    def __init__(self, value):
        self.type = type(self).__name__
        self.value = value
        print("making {} effect with value {}".format(self.type, value))

    def run(self):
        raise NotImplemented("Cannot run base Effect")


class Call(Effect):
    def __init__(self, fn, *args, **kwargs):
        super(Call, self).__init__((fn, args, kwargs))

    def run(self):
        fn, args, kwargs = self.value
        print("running call effect for fn", fn)
        return fn(*args, **kwargs)


class CallAsync(Call):
    def run(self):
        return lambda: super(CallAsync, self).run()


class Ret(Effect):
    def run(self):
        print("running ret effect with value", self.value)
        return self.value
