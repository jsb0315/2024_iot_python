import subprocess

TEST = "../TEST/TEST.ino"
RUN = "../RUN/RUN.ino"
arduino_port = "/dev/ttyACM0"

def compilecode(code, test = True):
    file_name = TEST if test else RUN
    print(file_name)
    # 아두이노 코드를 파일로 저장
    with open(file_name, 'w') as file:
        file.write(code)

    # 아두이노 코드 컴파일 명령어 실행
    compile_process = subprocess.Popen(['arduino-cli', 'compile', '--fqbn', 'arduino:avr:uno', file_name],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    output, error = compile_process.communicate()

    if compile_process.returncode == 0:
        return True
    else:
        print(error.decode('utf-8'))
        return False