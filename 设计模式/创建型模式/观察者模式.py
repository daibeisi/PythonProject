"""观察者模式实现，遵循Python最佳实践。

本模块演示了具有适当类型注解、文档、错误处理和Pythonic代码的观察者模式。
"""

from abc import ABC, abstractmethod
from typing import List, Any
import logging
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventType(Enum):
    """可以观察的事件类型枚举。"""
    STATE_CHANGED = "state_changed"
    DATA_UPDATED = "data_updated"
    OBJECT_CREATED = "object_created"


class Observer(ABC):
    """观察者的抽象基类。"""

    @abstractmethod
    def update(self, subject: 'Subject', event_type: EventType, data: Any = None) -> None:
        """接收来自主题的通知。

        参数:
            subject (Subject): 发送通知的主题。
            event_type (EventType): 发生的事件类型。
            data (Any, 可选): 与事件相关的附加数据。
        """
        pass


class Subject(ABC):
    """主题的抽象基类。"""

    def __init__(self) -> None:
        """用空的观察者列表初始化主题。"""
        self._observers: List[Observer] = []

    def attach(self, observer: Observer) -> None:
        """将观察者附加到主题。

        参数:
            observer (Observer): 要附加的观察者。

        异常:
            TypeError: 如果观察者不是Observer实例。
        """
        if not isinstance(observer, Observer):
            raise TypeError("观察者必须是Observer类的实例")
        
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info(f"附加了观察者 {observer.__class__.__name__}")

    def detach(self, observer: Observer) -> None:
        """从主题分离观察者。

        参数:
            observer (Observer): 要分离的观察者。
        """
        try:
            self._observers.remove(observer)
            logger.info(f"分离了观察者 {observer.__class__.__name__}")
        except ValueError:
            logger.warning(f"未找到观察者 {observer.__class__.__name__}")

    def notify(self, event_type: EventType, data: Any = None) -> None:
        """通知所有观察者事件。

        参数:
            event_type (EventType): 发生的事件类型。
            data (Any, 可选): 与事件相关的附加数据。
        """
        for observer in self._observers:
            try:
                observer.update(self, event_type, data)
            except Exception as e:
                logger.error(f"通知观察者 {observer.__class__.__name__} 时出错: {e}")


class WeatherData(Subject):
    """天气数据主题，用于通知观察者天气变化。"""

    def __init__(self) -> None:
        """用默认值初始化天气数据。"""
        super().__init__()
        self._temperature: float = 0.0
        self._humidity: float = 0.0
        self._pressure: float = 0.0

    @property
    def temperature(self) -> float:
        """获取当前温度。

        返回:
            float: 当前温度。
        """
        return self._temperature

    @property
    def humidity(self) -> float:
        """获取当前湿度。

        返回:
            float: 当前湿度。
        """
        return self._humidity

    @property
    def pressure(self) -> float:
        """获取当前气压。

        返回:
            float: 当前气压。
        """
        return self._pressure

    def set_measurements(self, temperature: float, humidity: float, pressure: float) -> None:
        """设置新的天气测量值并通知观察者。

        参数:
            temperature (float): 新的温度值。
            humidity (float): 新的湿度值。
            pressure (float): 新的气压值。
        """
        self._temperature = temperature
        self._humidity = humidity
        self._pressure = pressure
        self.measurements_changed()

    def measurements_changed(self) -> None:
        """当测量值改变时通知观察者。"""
        self.notify(EventType.STATE_CHANGED, {
            'temperature': self._temperature,
            'humidity': self._humidity,
            'pressure': self._pressure
        })


class CurrentConditionsDisplay(Observer):
    """显示当前天气状况。"""

    def __init__(self) -> None:
        """初始化显示器。"""
        self._temperature: float = 0.0
        self._humidity: float = 0.0

    def update(self, subject: Subject, event_type: EventType, data: Any = None) -> None:
        """使用新的天气数据更新显示器。

        参数:
            subject (Subject): 发送通知的主题。
            event_type (EventType): 发生的事件类型。
            data (Any, 可选): 与事件相关的附加数据。
        """
        if event_type == EventType.STATE_CHANGED and data:
            self._temperature = data.get('temperature', 0.0)
            self._humidity = data.get('humidity', 0.0)
            self.display()

    def display(self) -> None:
        """显示当前状况。"""
        print(f"当前状况: 温度{self._temperature}华氏度，湿度{self._humidity}%")


class StatisticsDisplay(Observer):
    """显示天气统计数据。"""

    def __init__(self) -> None:
        """用空的温度列表初始化显示器。"""
        self._temperatures: List[float] = []

    def update(self, subject: Subject, event_type: EventType, data: Any = None) -> None:
        """使用新的天气数据更新显示器。

        参数:
            subject (Subject): 发送通知的主题。
            event_type (EventType): 发生的事件类型。
            data (Any, 可选): 与事件相关的附加数据。
        """
        if event_type == EventType.STATE_CHANGED and data:
            self._temperatures.append(data.get('temperature', 0.0))
            self.display()

    def display(self) -> None:
        """显示统计数据。"""
        if not self._temperatures:
            print("没有可用的温度数据")
            return
            
        avg_temp = sum(self._temperatures) / len(self._temperatures)
        min_temp = min(self._temperatures)
        max_temp = max(self._temperatures)
        
        print(f"统计数据: 平均温度: {avg_temp:.1f}华氏度, "
              f"最低温度: {min_temp}华氏度, 最高温度: {max_temp}华氏度")


class ForecastDisplay(Observer):
    """根据气压变化显示天气预报。"""

    def __init__(self) -> None:
        """初始化显示器。"""
        self._current_pressure: float = 29.92  # 默认气压
        self._last_pressure: float = 0.0

    def update(self, subject: Subject, event_type: EventType, data: Any = None) -> None:
        """使用新的天气数据更新显示器。

        参数:
            subject (Subject): 发送通知的主题。
            event_type (EventType): 发生的事件类型。
            data (Any, 可选): 与事件相关的附加数据。
        """
        if event_type == EventType.STATE_CHANGED and data:
            self._last_pressure = self._current_pressure
            self._current_pressure = data.get('pressure', 29.92)
            self.display()

    def display(self) -> None:
        """显示预报。"""
        if self._current_pressure > self._last_pressure:
            forecast = "天气正在转好！"
        elif self._current_pressure == self._last_pressure:
            forecast = "天气保持不变"
        else:
            forecast = "注意天气转凉，可能有雨"
            
        print(f"天气预报: {forecast}")


def main() -> None:
    """演示观察者模式的实现。"""
    # 创建天气数据主题
    weather_data = WeatherData()
    
    # 创建观察者
    current_display = CurrentConditionsDisplay()
    statistics_display = StatisticsDisplay()
    forecast_display = ForecastDisplay()
    
    # 将观察者附加到主题
    weather_data.attach(current_display)
    weather_data.attach(statistics_display)
    weather_data.attach(forecast_display)
    
    # 模拟新的天气测量
    print("=== 天气站演示 ===")
    weather_data.set_measurements(80, 65, 30.4)
    print()
    weather_data.set_measurements(82, 70, 29.2)
    print()
    weather_data.set_measurements(78, 90, 29.2)
    
    # 分离一个观察者并再次更新
    print("\n=== 分离统计数据显示器 ===")
    weather_data.detach(statistics_display)
    weather_data.set_measurements(85, 60, 30.0)


if __name__ == "__main__":
    main()