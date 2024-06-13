import serial
import time

def verify_run(port, baudrate):
    mx = 0
    mn = 10000
    start_time = time.time()

    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            time.sleep(2)  # 보드 리셋 대기 시간
            print("Reading from serial port...")
            while time.time() - start_time < 7:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').rstrip()
                    line = line.replace('\r','').replace('VCC|','')
                    print(line)
                    if line.isdigit():
                        mx = mx if mx>int(line) else int(line)
                        mn = mn if mn<int(line) else int(line)
                        # print(mx, mn,mx-mn, line)
                        if 2*(mx-mn)/(mx+mn) > 0.03:
                            return False
            return True
    except serial.SerialException as e:
        print(f"Serial error: {e}")

if __name__ == "__main__":
    print(verify_run("/dev/ttyACM0",9600))