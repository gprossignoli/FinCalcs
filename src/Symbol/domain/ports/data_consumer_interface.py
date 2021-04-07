from abc import ABCMeta, abstractmethod


class DataConsumerInterface(metaclass=ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'connect') and
                callable(subclass.connect) and
                hasattr(subclass, 'disconnect') and
                callable(subclass.disconnect) and
                hasattr(subclass, 'on_message') and
                callable(subclass.on_message)) or NotImplemented

    @abstractmethod
    def connect(self):
        raise NotImplemented

    @abstractmethod
    def disconnect(self):
        raise NotImplemented

    @abstractmethod
    def on_message(self, *args):
        raise NotImplemented
