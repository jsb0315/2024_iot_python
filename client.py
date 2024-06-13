import asyncio, sys
import websockets, json, time
from compiler import compilecode
from uploader import uploadcode
from verify import verify_run

arduino_port = "/dev/ttyACM0"

tmp1 = '''void setup() {
    Serial.begin(9600);'''
tmp2 = '''Serial.print("VCC|");
    Serial.println(readVcc());
    delay('''
tmp3 = '''
long readVcc() {
  #if defined(__AVR_ATmega32U4__) || defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__)
    ADMUX = _BV(REFS0) | _BV(MUX4) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  #elif defined (__AVR_ATtiny24__) || defined(__AVR_ATtiny44__) || defined(__AVR_ATtiny84__)
    ADMUX = _BV(MUX5) | _BV(MUX0);
  #elif defined (__AVR_ATtiny25__) || defined(__AVR_ATtiny45__) || defined(__AVR_ATtiny85__)
    ADMUX = _BV(MUX3) | _BV(MUX2);
  #else
    ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  #endif  

  delay(2);                        // Wait for Vref to settle

  ADCSRA |= _BV(ADSC);             // Start conversion
  while (bit_is_set(ADCSRA,ADSC)); // measuring

  uint8_t low  = ADCL;             // must read ADCL first - it then locks ADCH  
  uint8_t high = ADCH;             // unlocks both

  long result = (high<<8) | low;

  result = 1125300L / result;      // Calculate Vcc (in mV); 1125300 = 1.1*1023*1000
  // result = result * 5070 / 5271; // Calibraiton Equation (= result * true Vcc / reading Vcc)

  return result; // Vcc in millivolts
}'''

async def communicate(room):
    uri = "ws://203.234.62.169:8080"
    async with websockets.connect(uri) as websocket:
        # 사용자로부터 닉네임과 채팅방 이름 입력
        nickname = "UNO"
        
        # 서버로 채팅방 참여 요청 전송
        message = '{"type": "%s", "room": "%s", "user": "%s", "content": "%s", "value": "%s"}'
        response = { 'type': '', 'room': '', 'content': '', 'user': '', 'value': '' }

        stat = "join"
        content = "connection"
        value = "connected"
        print("Wating...")
        
        while True:
            if response['type'] == 'leave':
                print("Wating...")
            # 만약 사용자가 'Q'를 입력하면 루프를 종료하고 연결을 종료함
            if content.upper() == "Q":
                await websocket.send(message % ("leave", room, nickname, "connection", ""))
                break
            
            # 서버로 메시지 전송
            if response['type'] != 'leave':
                await websocket.send(message % (stat, room, nickname, content, value))
            
            # 서버로부터 응답 수신
            response = json.loads(await websocket.recv())
            print(f"서버 응답: {response}")
            if response['type'] == 'message' and response['user'] != nickname:
                stat = "message"
                if response['content'] == 'connection':
                    content = "registration"
                    value = "wait registration"
                    print(value)
                elif response['content'] == "registration":
                    print("Compiling...")
                    content = "compile" #업로드 컴파일 동시진행해야댐
                    res = response['value'].replace("<<", "").replace(">>", "").replace("void setup() {", tmp1).replace('delay(', tmp2) + tmp3
                    value = compilecode(res) and uploadcode(True)
                    if value:
                        compilecode(res, False)
                        uploadcode(False)
                        print("Uploading...")
                    print(value)
                elif response['content'] == "verify":
                    print("Verifing...")
                    content = "verify"
                    value = verify_run(arduino_port, 9600)
                    print("overVoltage:",value)
            elif response['type'] == 'join':
                stat = "message"
            elif response['type'] == 'err':
                await websocket.send(message % ("err", room, nickname, "err", "Already exists."))
                break


        await websocket.send(message % ("leave", room, nickname, "stat", ""))

if __name__ == "__main__":
    name = "IOT101"
    if len(sys.argv) > 1:
        name = sys.argv[1]
    while(True):
        try:
            print(f'Tring Connection: "{name}"')
            asyncio.run(communicate(name))
        except KeyboardInterrupt: 
            print("Disconnected")
        except websockets.exceptions.ConnectionClosedError: 
            print("Server shut down")
        except TimeoutError:
            print("Server not started")
        except ConnectionRefusedError:
            print("Server not started")
        time.sleep(10)
