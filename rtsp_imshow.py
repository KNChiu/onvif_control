import time
import cv2 
import time

userName = 'admin'
passWord = 'mirdc83300307'
ip = '192.168.0.237'

RTSP = r'rtsp://' + str(userName) + ':' + str(passWord) + '@' + str(ip) + "/stream1"


# RTSP = r"rtsp://admin:mirdc83300307@192.168.0.237:554/stream1"
# # RTSP = r"rtsp://admin:mirdc83300307@192.168.0.237:554/stream2"


start = time.time()

def work_with_captured_video(camera):
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Camera is disconnected!")
            camera.release()
            return False
        else:
            cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    return True


while True:
    try :
        camera = cv2.VideoCapture(RTSP)
        if camera.isOpened():
            print('Camera is connected')
            response = work_with_captured_video(camera)
            if response == False:
                time.sleep(0.5)
                continue
            else:
                break
        else:
            print('Camera not connected')
            camera.release()
            time.sleep(0.5)
            continue
    except Exception as e:
        print('erro :',e)
        time.sleep(0.5)
        continue
