import time
import cv2 
import time

userName = 'admin'                      
passWord = 'mirdc83300307'
ip = '192.168.0.237'

# 設定 RTSP 連線網址
RTSP = r'rtsp://' + str(userName) + ':' + str(passWord) + '@' + str(ip) + "/stream1"

def rtsp_captured_video(camera):       # 將畫面解析並輸出全螢幕
    while True:
        ret, frame = camera.read()              # 取得影像
        if not ret:                             # 如果斷線
            print("Camera is disconnected!")
            camera.release()                    # 釋放資源
            return False                        # 回傳錯誤斷線旗標
        else:
            # 全螢幕顯示
            cv2.namedWindow('onvif camera', cv2.WINDOW_NORMAL)                                          
            cv2.setWindowProperty('onvif camera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)       
            cv2.imshow('onvif camera', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):   # 按下鍵盤 q 跳出
            break
    return True                                 # 回傳正確退出旗標



if __name__ == '__main__':
    while True:
        try :
            camera = cv2.VideoCapture(RTSP)
            if camera.isOpened():                           # 判斷影像是否開啟
                print('Camera is connected')
                response = rtsp_captured_video(camera)      # 進入串流副程式
                if response == False:                       # 如果意外斷線嘗試重新連線
                    time.sleep(0.5)                         # 等待 0.5秒 重連
                    continue
                else:
                    break                                   # 如果正常退出結束程式
            else:
                print('Camera not connected')
                camera.release()                            # 釋放資源  
                time.sleep(0.5)                             
                continue                                    

        except Exception as e:
            print('erro :',e)
            time.sleep(0.5)
            continue
