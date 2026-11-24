import machine
import math

class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')  # Despertar el MPU6050

    def read_accel_gyro(self):
        # Leemos 14 bytes de datos desde el MPU6050
        data = self.i2c.readfrom_mem(self.addr, 0x3B, 14)
        
        # Acelerómetro (2 bytes por eje)
        accel_x = int.from_bytes(data[0:2], 'big') if data[0] < 128 else int.from_bytes(data[0:2], 'big') - 65536
        accel_y = int.from_bytes(data[2:4], 'big') if data[2] < 128 else int.from_bytes(data[2:4], 'big') - 65536
        accel_z = int.from_bytes(data[4:6], 'big') if data[4] < 128 else int.from_bytes(data[4:6], 'big') - 65536
        
        # Giroscopio (2 bytes por eje)
        gyro_x = int.from_bytes(data[8:10], 'big') if data[8] < 128 else int.from_bytes(data[8:10], 'big') - 65536
        gyro_y = int.from_bytes(data[10:12], 'big') if data[10] < 128 else int.from_bytes(data[10:12], 'big') - 65536
        gyro_z = int.from_bytes(data[12:14], 'big') if data[12] < 128 else int.from_bytes(data[12:14], 'big') - 65536

        return {
            'AcX': accel_x, 
            'AcY': accel_y, 
            'AcZ': accel_z,
            'GyX': gyro_x, 
            'GyY': gyro_y, 
            'GyZ': gyro_z
        }
