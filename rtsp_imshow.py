import time
import cv2 
import time
start = time.time()

RTSP = r"rtsp://admin:mirdc83300307@192.168.0.237:554/stream1"
# RTSP = r"rtsp://admin:mirdc83300307@192.168.0.237:554/stream2"


cap = cv2.VideoCapture(RTSP)

start = time.time()

while True:
    ret, frame = cap.read()

    if ret:
        cv2.imshow("frame",frame)
        ch = cv2.waitKey(1)
        
        if ch == 27 or ch == ord('q') or ch == ord('Q'):
            break
    else: 
        break

    end = time.time()
    print("FPS：%f " % (1/(end - start)))

cv2.destroyAllWindows()
cap.release()
print(time.time()-start)