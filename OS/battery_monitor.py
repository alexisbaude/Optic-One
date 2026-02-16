#!/usr/bin/env python3
"""
Battery Management System for Optic One
Monitors battery health, voltage, current, and provides alerts
"""

import time
import logging
import threading
from typing import Optional, Dict, Callable, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

try:
    import smbus2
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False
    logging.warning("smbus2 not available - battery monitoring limited")


class BatteryStatus(Enum):
    """Battery status enumeration"""
    UNKNOWN = "unknown"
    CHARGING = "charging"
    DISCHARGING = "discharging"
    FULL = "full"
    LOW = "low"
    CRITICAL = "critical"


@dataclass
class BatteryReading:
    """Battery status snapshot"""
    timestamp: datetime
    voltage: float
    current: float
    percentage: int
    status: BatteryStatus
    temperature: Optional[float]
    health: int  # 0-100
    cycle_count: Optional[int]
    time_remaining: Optional[int]  # minutes


class BatteryMonitor:
    """
    Advanced battery monitoring system with health tracking
    Supports multiple battery backends: I2C HAT, GPIO ADC, system interface
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.monitor_interval = config.get('monitor_interval', 30)
        self.low_threshold = config.get('low_battery_threshold', 20)
        self.critical_threshold = config.get('critical_battery_threshold', 10)
        
        # Hardware interface
        self.i2c_address = config.get('i2c_address')
        self.voltage_pin = config.get('voltage_pin')
        self.current_pin = config.get('current_pin')
        
        # Monitoring state
        self.running = False
        self.monitor_thread = None
        self.current_reading: Optional[BatteryReading] = None
        
        # Alert callbacks
        self.alert_callbacks: List[Callable] = []
        
        # History
        self.history: List[BatteryReading] = []
        self.max_history = 1000
        
        # Battery backend
        self.backend = self._detect_backend()
        
        logging.info(f"Battery monitor initialized (backend: {self.backend})")
    
    def _detect_backend(self) -> str:
        """Detect available battery monitoring backend"""
        if self.i2c_address and SMBUS_AVAILABLE:
            return "i2c"
        elif self._check_system_battery():
            return "system"
        elif self.voltage_pin:
            return "gpio"
        else:
            return "simulated"
    
    def _check_system_battery(self) -> bool:
        """Check if system battery interface is available"""
        try:
            with open('/sys/class/power_supply/battery/capacity', 'r') as f:
                f.read()
            return True
        except:
            return False
    
    def start_monitoring(self):
        """Start battery monitoring in background thread"""
        if not self.enabled:
            logging.info("Battery monitoring disabled in config")
            return
        
        if self.running:
            logging.warning("Battery monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="BatteryMonitor"
        )
        self.monitor_thread.start()
        logging.info("Battery monitoring started")
    
    def stop_monitoring(self):
        """Stop battery monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logging.info("Battery monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                reading = self._read_battery()
                
                if reading:
                    self.current_reading = reading
                    self._add_to_history(reading)
                    self._check_alerts(reading)
                
                time.sleep(self.monitor_interval)
                
            except Exception as e:
                logging.error(f"Battery monitoring error: {e}")
                time.sleep(self.monitor_interval)
    
    def _read_battery(self) -> Optional[BatteryReading]:
        """Read battery status from appropriate backend"""
        if self.backend == "i2c":
            return self._read_i2c()
        elif self.backend == "system":
            return self._read_system()
        elif self.backend == "gpio":
            return self._read_gpio()
        else:
            return self._read_simulated()
    
    def _read_i2c(self) -> Optional[BatteryReading]:
        """Read battery from I2C HAT (e.g., PiSugar, UPS HAT)"""
        try:
            bus = smbus2.SMBus(1)
            
            # Example for PiSugar 2
            # Adjust register addresses for your specific HAT
            voltage_reg = 0x22
            current_reg = 0x26
            percentage_reg = 0x2A
            
            voltage_raw = bus.read_word_data(self.i2c_address, voltage_reg)
            current_raw = bus.read_word_data(self.i2c_address, current_reg)
            percentage = bus.read_byte_data(self.i2c_address, percentage_reg)
            
            voltage = voltage_raw / 1000.0  # Convert to volts
            current = current_raw / 1000.0  # Convert to amps
            
            # Determine status
            if percentage >= 99:
                status = BatteryStatus.FULL
            elif current > 0:
                status = BatteryStatus.CHARGING
            elif percentage <= self.critical_threshold:
                status = BatteryStatus.CRITICAL
            elif percentage <= self.low_threshold:
                status = BatteryStatus.LOW
            else:
                status = BatteryStatus.DISCHARGING
            
            # Calculate time remaining
            if current < 0:  # Discharging
                # Assume 2500mAh battery
                capacity_remaining = 2500 * (percentage / 100)
                time_remaining = int((capacity_remaining / abs(current)) * 60)
            else:
                time_remaining = None
            
            return BatteryReading(
                timestamp=datetime.now(),
                voltage=voltage,
                current=current,
                percentage=percentage,
                status=status,
                temperature=None,
                health=100,  # Would need additional logic
                cycle_count=None,
                time_remaining=time_remaining
            )
            
        except Exception as e:
            logging.error(f"I2C battery read error: {e}")
            return None
    
    def _read_system(self) -> Optional[BatteryReading]:
        """Read battery from system interface"""
        try:
            with open('/sys/class/power_supply/battery/capacity', 'r') as f:
                percentage = int(f.read().strip())
            
            with open('/sys/class/power_supply/battery/status', 'r') as f:
                status_str = f.read().strip().lower()
            
            # Map system status to our enum
            status_map = {
                'charging': BatteryStatus.CHARGING,
                'discharging': BatteryStatus.DISCHARGING,
                'full': BatteryStatus.FULL,
                'not charging': BatteryStatus.DISCHARGING
            }
            status = status_map.get(status_str, BatteryStatus.UNKNOWN)
            
            # Override based on percentage
            if percentage <= self.critical_threshold:
                status = BatteryStatus.CRITICAL
            elif percentage <= self.low_threshold:
                status = BatteryStatus.LOW
            
            # Try to read voltage
            try:
                with open('/sys/class/power_supply/battery/voltage_now', 'r') as f:
                    voltage = int(f.read().strip()) / 1000000.0  # µV to V
            except:
                voltage = 3.7  # Nominal voltage
            
            # Try to read current
            try:
                with open('/sys/class/power_supply/battery/current_now', 'r') as f:
                    current = int(f.read().strip()) / 1000000.0  # µA to A
            except:
                current = 0.0
            
            return BatteryReading(
                timestamp=datetime.now(),
                voltage=voltage,
                current=current,
                percentage=percentage,
                status=status,
                temperature=None,
                health=100,
                cycle_count=None,
                time_remaining=None
            )
            
        except Exception as e:
            logging.error(f"System battery read error: {e}")
            return None
    
    def _read_gpio(self) -> Optional[BatteryReading]:
        """Read battery from GPIO ADC"""
        # Would require ADC chip (e.g., MCP3008)
        # Not implemented in this version
        logging.warning("GPIO battery monitoring not implemented")
        return None
    
    def _read_simulated(self) -> BatteryReading:
        """Return simulated battery reading for testing"""
        import random
        
        # Simulate slow discharge
        if self.current_reading:
            percentage = max(0, self.current_reading.percentage - random.randint(0, 1))
        else:
            percentage = 85
        
        if percentage <= self.critical_threshold:
            status = BatteryStatus.CRITICAL
        elif percentage <= self.low_threshold:
            status = BatteryStatus.LOW
        else:
            status = BatteryStatus.DISCHARGING
        
        return BatteryReading(
            timestamp=datetime.now(),
            voltage=3.7,
            current=-0.5,
            percentage=percentage,
            status=status,
            temperature=35.0,
            health=95,
            cycle_count=42,
            time_remaining=int(percentage * 2)
        )
    
    def _add_to_history(self, reading: BatteryReading):
        """Add reading to history"""
        self.history.append(reading)
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def _check_alerts(self, reading: BatteryReading):
        """Check if alerts should be triggered"""
        if not self.config.get('alert_enabled', True):
            return
        
        # Low battery alert
        if reading.status == BatteryStatus.LOW:
            self._trigger_alert('low_battery', reading)
        
        # Critical battery alert
        elif reading.status == BatteryStatus.CRITICAL:
            self._trigger_alert('critical_battery', reading)
        
        # Charging complete
        elif reading.status == BatteryStatus.FULL:
            self._trigger_alert('battery_full', reading)
    
    def _trigger_alert(self, alert_type: str, reading: BatteryReading):
        """Trigger alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alert_type, reading)
            except Exception as e:
                logging.error(f"Alert callback error: {e}")
    
    def register_alert_callback(self, callback: Callable):
        """Register callback for battery alerts"""
        self.alert_callbacks.append(callback)
    
    def get_status(self) -> Optional[BatteryReading]:
        """Get current battery status"""
        return self.current_reading
    
    def get_percentage(self) -> int:
        """Get current battery percentage"""
        if self.current_reading:
            return self.current_reading.percentage
        return 0
    
    def get_health_report(self) -> Dict:
        """Generate battery health report"""
        if not self.history:
            return {"status": "no_data"}
        
        recent = self.history[-100:]  # Last 100 readings
        
        avg_voltage = sum(r.voltage for r in recent) / len(recent)
        avg_current = sum(r.current for r in recent) / len(recent)
        
        # Calculate discharge rate
        if len(recent) > 1:
            time_span = (recent[-1].timestamp - recent[0].timestamp).total_seconds() / 60
            percentage_change = recent[0].percentage - recent[-1].percentage
            discharge_rate = percentage_change / time_span if time_span > 0 else 0
        else:
            discharge_rate = 0
        
        return {
            "status": "healthy",
            "current_percentage": self.current_reading.percentage,
            "average_voltage": round(avg_voltage, 2),
            "average_current": round(avg_current, 3),
            "discharge_rate": round(discharge_rate, 2),  # % per minute
            "health_score": self.current_reading.health if self.current_reading else 100,
            "readings_count": len(self.history),
            "backend": self.backend
        }
    
    def is_healthy(self) -> bool:
        """Check if battery is functioning normally"""
        if not self.current_reading:
            return False
        
        # Check voltage in safe range (for Li-Po: 3.0V - 4.2V)
        if self.current_reading.voltage < 3.0 or self.current_reading.voltage > 4.3:
            return False
        
        # Check if battery percentage makes sense
        if self.current_reading.percentage < 0 or self.current_reading.percentage > 100:
            return False
        
        return True
