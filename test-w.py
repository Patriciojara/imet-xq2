import serial

ser = serial.Serial()

ser.port = "COM12"
ser.baudrate = 57600
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.timeout = 2

# Sin control de flujo
ser.xonxoff = False
ser.rtscts = False
ser.dsrdtr = False

# Evitamos activar innecesariamente estas líneas
ser.dtr = False
ser.rts = False

ser.open()

print("Puerto abierto:", ser.port)

while True:

    data = ser.readline()

    if data:
        print(repr(data))