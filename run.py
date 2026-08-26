import csv
import sys
from datetime import datetime
from pathlib import Path

import serial
from serial.tools import list_ports


# ============================================================
# CONFIGURACIÓN
# ============================================================

BAUDRATE = 57600
TIMEOUT = 2

# Si quieres forzar manualmente un puerto, escribe por ejemplo:
# MANUAL_PORT = "COM4"
# MANUAL_PORT = "/dev/ttyUSB0"
#
# Si se deja en None, el programa intenta encontrar automáticamente
# el adaptador FTDI del iMet-XQ2.
MANUAL_PORT = None

# Adaptador FTDI detectado para el iMet-XQ2
FTDI_VID = 0x0403
FTDI_PID = 0x6015


# ============================================================
# RUTAS
# ============================================================

# main.py está en:
# imet-xq2/src/main.py
#
# Por eso parent.parent corresponde a la raíz del proyecto.

SCRIPT_DIR = Path(__file__).resolve().parent

DATA_DIR = SCRIPT_DIR / "data"

DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# COLUMNAS DEL CSV
# ============================================================

CSV_COLUMNS = [
    "host_timestamp",
    "sensor_datetime_utc",

    "pressure_raw_pa",
    "pressure_hpa",

    "temperature_raw",
    "temperature_c",

    "humidity_raw",
    "relative_humidity_ratio",
    "relative_humidity_pct",

    "humidity_temperature_raw",
    "humidity_temperature_c",

    "longitude_raw",
    "longitude_deg",

    "latitude_raw",
    "latitude_deg",

    "altitude_raw_mm",
    "altitude_m",

    "satellites",

    "adc_1",
    "adc_2",
    "adc_3",
    "adc_4",
    "adc_5",
    "adc_6",
    "adc_7",
    "adc_8",

    "parse_ok",
    "raw_data",
    "raw_hex",
]


# ============================================================
# DETECCIÓN DEL PUERTO SERIAL
# ============================================================

def find_serial_port():
    """
    Busca automáticamente el adaptador FTDI usado por el iMet-XQ2.

    Si MANUAL_PORT está definido, utiliza ese puerto directamente.
    """

    if MANUAL_PORT is not None:
        return MANUAL_PORT

    ports = list(list_ports.comports())

    # Primero buscamos exactamente el FTDI 0403:6015
    for port in ports:
        if port.vid == FTDI_VID and port.pid == FTDI_PID:
            print(
                f"[OK] iMet-XQ2 detectado: "
                f"{port.device} - {port.description}"
            )
            return port.device

    # Si no encontramos el FTDI, pero hay un único puerto,
    # mostramos información para ayudar a diagnosticar.
    if len(ports) == 1:
        port = ports[0]

        print("[AVISO] No se encontró el VID/PID esperado.")
        print(f"[AVISO] Único puerto disponible: {port.device}")
        print(f"[AVISO] Descripción: {port.description}")

        return port.device

    print("\n[ERROR] No fue posible identificar automáticamente el iMet-XQ2.")

    if ports:
        print("\nPuertos seriales disponibles:")

        for port in ports:
            vid = f"{port.vid:04X}" if port.vid is not None else "----"
            pid = f"{port.pid:04X}" if port.pid is not None else "----"

            print(
                f"  {port.device:<10} "
                f"VID:PID={vid}:{pid} "
                f"{port.description}"
            )

        print(
            "\nPuedes definir el puerto manualmente modificando "
            "MANUAL_PORT al inicio del programa."
        )

    else:
        print("No hay puertos seriales disponibles.")

    return None


# ============================================================
# CREAR ARCHIVO CSV
# ============================================================

def create_csv_file():
    """
    Genera un nombre único basado en la fecha y hora de inicio.
    """

    now = datetime.now()

    filename = DATA_DIR / (
        f"imet_{now:%Y-%m-%d_%H-%M-%S}.csv"
    )

    return filename


# ============================================================
# DATOS VACÍOS
# ============================================================

def empty_record():
    """
    Crea un registro vacío con todas las columnas.
    """

    return {column: "" for column in CSV_COLUMNS}


# ============================================================
# PARSER DEL iMet-XQ2
# ============================================================

def parse_imet(raw_text, raw_bytes):
    """
    Convierte una trama del iMet-XQ2 en variables físicas.

    Formato esperado a partir de XQ:

    XQ,
    pressure,
    temperature,
    humidity,
    humidity_temperature,
    date,
    time,
    longitude,
    latitude,
    altitude,
    satellites

    También admite 8 canales ADC antes de XQ.
    """

    record = empty_record()

    # Timestamp generado por el computador/Raspberry Pi
    record["host_timestamp"] = (
        datetime.now()
        .astimezone()
        .isoformat(timespec="milliseconds")
    )

    # Siempre guardamos los datos originales
    record["raw_data"] = raw_text
    record["raw_hex"] = raw_bytes.hex(" ")
    record["parse_ok"] = False

    try:
        fields = [field.strip() for field in raw_text.split(",")]

        # Encontrar dónde comienza la información XQ
        #xq_index = fields.index("XQ")


        xq_index = None

        for i, field in enumerate(fields):
            if "XQ" in field:
                xq_index = i
                break

        # Si no contiene XQ, conservamos los datos crudos
        # pero no lo consideramos un error del programa.
        if xq_index is None:
            return record



        # ----------------------------------------------------
        # ADC opcional
        # ----------------------------------------------------

        adc_fields = fields[:xq_index]

        # Si vienen 8 valores ADC, los guardamos
        if len(adc_fields) >= 8:
            last_8_adc = adc_fields[-8:]

            for i, value in enumerate(last_8_adc, start=1):
                try:
                    record[f"adc_{i}"] = float(value)
                except ValueError:
                    record[f"adc_{i}"] = value

        # ----------------------------------------------------
        # DATOS DEL iMet
        # ----------------------------------------------------

        imet = fields[xq_index + 1:]

        if len(imet) < 10:
            raise ValueError(
                f"Trama XQ incompleta: se esperaban al menos "
                f"10 campos y llegaron {len(imet)}."
            )

        pressure_raw = int(imet[0])
        temperature_raw = int(imet[1])
        humidity_raw = int(imet[2])
        humidity_temperature_raw = int(imet[3])

        sensor_date = imet[4]
        sensor_time = imet[5]

        longitude_raw = int(imet[6])
        latitude_raw = int(imet[7])
        altitude_raw = int(imet[8])
        satellites = int(imet[9])

        # ----------------------------------------------------
        # CONVERSIONES
        # ----------------------------------------------------

        # Presión
        # dato original: Pa
        pressure_hpa = pressure_raw / 100.0

        # Temperatura
        # dato original: centésimas de °C
        temperature_c = temperature_raw / 100.0

        # Humedad
        #
        # El valor documentado puede interpretarse como una razón
        # en milésimas.
        #
        # Ejemplo:
        # 499 -> 0.499 -> 49.9 %
        humidity_ratio = humidity_raw / 1000.0
        humidity_pct = humidity_ratio * 100.0

        # Temperatura asociada al sensor de humedad
        humidity_temperature_c = (
            humidity_temperature_raw / 100.0
        )

        # Coordenadas GPS:
        # unidades de 10^-7 grados
        longitude_deg = longitude_raw / 10_000_000.0
        latitude_deg = latitude_raw / 10_000_000.0

        # Altitud:
        # milímetros sobre nivel del mar
        altitude_m = altitude_raw / 1000.0

        # ----------------------------------------------------
        # FECHA / HORA UTC DEL SENSOR
        # ----------------------------------------------------

        try:
            sensor_datetime = datetime.strptime(
                f"{sensor_date} {sensor_time}",
                "%Y/%m/%d %H:%M:%S",
            )

            sensor_datetime_utc = (
                sensor_datetime.strftime("%Y-%m-%dT%H:%M:%SZ")
            )

        except ValueError:
            # Conservamos igualmente la información si el formato
            # cambia ligeramente.
            sensor_datetime_utc = (
                f"{sensor_date} {sensor_time}"
            )

        # ----------------------------------------------------
        # GUARDAR EN REGISTRO
        # ----------------------------------------------------

        record.update(
            {
                "sensor_datetime_utc": sensor_datetime_utc,

                "pressure_raw_pa": pressure_raw,
                "pressure_hpa": pressure_hpa,

                "temperature_raw": temperature_raw,
                "temperature_c": temperature_c,

                "humidity_raw": humidity_raw,
                "relative_humidity_ratio": humidity_ratio,
                "relative_humidity_pct": humidity_pct,

                "humidity_temperature_raw":
                    humidity_temperature_raw,

                "humidity_temperature_c":
                    humidity_temperature_c,

                "longitude_raw": longitude_raw,
                "longitude_deg": longitude_deg,

                "latitude_raw": latitude_raw,
                "latitude_deg": latitude_deg,

                "altitude_raw_mm": altitude_raw,
                "altitude_m": altitude_m,

                "satellites": satellites,

                "parse_ok": True,
            }
        )

    except (ValueError, IndexError) as error:
        # No eliminamos la lectura.
        # Sigue quedando almacenada en raw_data y raw_hex.
        record["parse_ok"] = False

        print(f"[AVISO] No se pudo interpretar la trama: {error}")

    return record


# ============================================================
# MOSTRAR DATOS EN TERMINAL
# ============================================================

def print_record(record):
    """
    Muestra una lectura de forma legible.
    """

    if not record["parse_ok"]:
        print(
            f"[OTHER] "
            f"RAW={record['raw_data']!r} | "
            f"HEX={record['raw_hex']}"
        )
        return

    print(
        f"{record['sensor_datetime_utc']} | "
        f"T: {record['temperature_c']:.2f} °C | "
        f"RH: {record['relative_humidity_pct']:.1f} % | "
        f"P: {record['pressure_hpa']:.2f} hPa | "
        f"Lat: {record['latitude_deg']:.7f} | "
        f"Lon: {record['longitude_deg']:.7f} | "
        f"Alt: {record['altitude_m']:.2f} m | "
        f"Sat: {record['satellites']}"
    )


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("=" * 75)
    print("                    iMet-XQ2 DATA LOGGER")
    print("=" * 75)

    # --------------------------------------------------------
    # BUSCAR PUERTO
    # --------------------------------------------------------

    serial_port = find_serial_port()

    if serial_port is None:
        sys.exit(1)

    # --------------------------------------------------------
    # CREAR ARCHIVO CSV
    # --------------------------------------------------------

    csv_path = create_csv_file()

    print(f"\nPuerto     : {serial_port}")
    print(f"Baudrate   : {BAUDRATE}")
    print(f"Archivo CSV: {csv_path}")
    print("\nPresiona Ctrl+C para detener la adquisición.\n")

    # --------------------------------------------------------
    # ABRIR PUERTO SERIAL
    # --------------------------------------------------------

    try:
        ser = serial.Serial(
            port=serial_port,
            baudrate=BAUDRATE,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT,
        )

    except serial.SerialException as error:
        print(f"[ERROR] No se pudo abrir {serial_port}")
        print(error)
        sys.exit(1)

    # Limpiar datos que hayan quedado previamente en el buffer
    ser.reset_input_buffer()

    # --------------------------------------------------------
    # ABRIR CSV
    # --------------------------------------------------------

    samples = 0

    try:
        with open(
            csv_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=CSV_COLUMNS,
            )

            writer.writeheader()
            csv_file.flush()

            print("[OK] Adquisición iniciada.\n")

            # ------------------------------------------------
            # LOOP DE ADQUISICIÓN
            # ------------------------------------------------

            while True:

                raw_bytes = ser.readline()

                # Timeout sin recibir datos
                if not raw_bytes:
                    continue

                # Eliminar CR/LF
                clean_bytes = raw_bytes.rstrip(b"\r\n")

                if not clean_bytes:
                    continue

                # Decodificar texto sin perder el programa
                # ante caracteres inválidos
                raw_text = clean_bytes.decode(
                    "ascii",
                    errors="replace",
                )

                # Interpretar trama
                record = parse_imet(
                    raw_text,
                    clean_bytes,
                )

                # Guardar CSV
                writer.writerow(record)

                # Escribimos físicamente en disco después
                # de cada muestra para reducir pérdidas de datos
                # si el programa se interrumpe.
                csv_file.flush()

                samples += 1

                # Mostrar en pantalla
                print_record(record)

    except KeyboardInterrupt:
        print("\n\nAdquisición detenida por el usuario.")

    except serial.SerialException as error:
        print("\n[ERROR] Error durante la comunicación serial:")
        print(error)

    finally:
        if ser.is_open:
            ser.close()

        print("\n" + "=" * 75)
        print(f"Muestras registradas : {samples}")
        print(f"Archivo              : {csv_path}")
        print("Puerto serial cerrado.")
        print("=" * 75)


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()