import math

def combine_value(high_byte, low_byte):
    """ 合并高8位和低8位
    :param high_byte: 高字节
    :param low_byte: 低字节
    :return: 合并值
    """
    return (high_byte << 8) | low_byte


def convert_voltage(value):
    """ 将采样数据转换为电压
    :param value: 采样值
    :return: 实际值
    """
    return round(value * 0.0015 * 1 - 0.768, 3)

def R2T(R):
    a = -5.721
    b = 4445.254
    c = -59650.499
    T = (2 * c) / (-b + math.sqrt(b**2 - 4 * c * (a - math.log(R)))) - 273.15
    return T


class ObserverVoltageSet:
    def update(self, val):
        print("er vol_set: ", val)


class ObservedVoltageSet:
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)

    def detach(self, observer):
        try:
            self.observers.remove(observer)
        except ValueError:
            pass

    def notify(self, val):
        for observer in self.observers:
            observer.update(val)

