import serial

ser = serial.Serial(
    port="/dev/ttyUSB0",
    baudrate=57600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=2,
    xonxoff=False,
    rtscts=False,
    dsrdtr=False
)

ser.dtr = False
ser.rts = False

print("Leyendo iMet-XQ2...\n")

try:
    while True:
        data = ser.readline()

        if data:
            print(repr(data))

except KeyboardInterrupt:
    print("\nLectura detenida.")

finally:
    ser.close()