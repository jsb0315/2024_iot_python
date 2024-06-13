import subprocess

TEST = "../TEST/TEST.ino"
RUN = "../RUN/RUN.ino"
arduino_port = "/dev/ttyACM0"

def uploadcode(test = True):
    file_name = TEST if test else RUN
    print(file_name)
    # 아두이노에 코드 업로드
    upload_process = subprocess.Popen(['arduino-cli', 'upload', '-p', arduino_port, '--fqbn', 'arduino:avr:uno', file_name],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
    output, error = upload_process.communicate()

    if upload_process.returncode == 0:
        return True
    else:
        print(error.decode('utf-8'))
        return False