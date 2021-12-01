import time
import cv2 
from onvif import ONVIFCamera
import zeep


def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue

class Onvif_control():
    def __init__(self, ip: str, port: str, username: str, password: str):    # 基本參數
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue

        try:
            self.mycam = ONVIFCamera(self.ip, self.port, self.username, self.password)
            self.media = self.mycam.create_media_service()          # 建立媒體服務
            self.media_profile = self.media.GetProfiles()[0]        # 獲取配置訊息
            self.ptz = self.mycam.create_ptz_service()              # 建立控制服務

            self.resp = self.mycam.devicemgmt.GetHostname()         # 取得 hostname
            dt = self.mycam.devicemgmt.GetSystemDateAndTime()       # 獲取系統日期和時間

            # ================ 時間取得 ================
            tz = dt.TimeZone.TZ

            year = dt.LocalDateTime.Date.Year               
            Month = dt.LocalDateTime.Date.Month
            Day = dt.LocalDateTime.Date.Day

            hour = dt.LocalDateTime.Time.Hour
            Minute = dt.LocalDateTime.Time.Minute
            Second = dt.LocalDateTime.Time.Second

            print("==========初始化==========")
            print('Hostname: ' + str(self.resp.Name))
            print("IP: %s:%s"  %(self.ip, self.port))
            print("時區:" , tz)
            print("日期: %s/%s/%s"  %(year, Month, Day))
            print("時間: %s:%s:%s"  %(hour, Minute, Second))
            print("==========初始化完成==========")

            # ================ 時間取得 ================


        except Exception as e:
            print('erro :',e)
    
    def continuous_move(self):                          # 連續移動控制
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        request = self.ptz.create_type('ContinuousMove')                         # 連續移動模式
        request.ProfileToken = self.media_profile.token
        # self.ptz.Stop({'ProfileToken': self.media_profile.token})

        # Get PTZ status
        if request.Velocity is None:
            request.Velocity = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
            request.Velocity.PanTilt.space = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].URI
            request.Velocity.Zoom.space = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].URI
        
        # Get range of pan and tilt
        # NOTE: X and Y are velocity vector
        global XMAX, XMIN, YMAX, YMIN
        XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
        # print(ptz_configuration_options)
        return request

    def perform_move(self, ptz, request, timeout):      # 移動命令
        ptz.ContinuousMove(request)
        time.sleep(timeout)                             # 移動延遲時間
        ptz.Stop({'ProfileToken': request.ProfileToken})    # 停止移動
 
    def move_up(self, ptz, request, timeout=1):         # 上移
        print('move up...') 
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = YMAX
        self.perform_move(ptz, request, timeout)
    
    def move_down(self, ptz, request, timeout=1):       # 下移
        print('move down...') 
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = YMIN
        self.perform_move(ptz, request, timeout)
    
    def move_right(self, ptz, request, timeout=1):      # 右移
        print('move right...') 
        request.Velocity.PanTilt.x = XMAX
        request.Velocity.PanTilt.y = 0
        self.perform_move(ptz, request, timeout)
    
    def move_left(self, ptz, request, timeout=1):       # 左移
        print('move left...') 
        request.Velocity.PanTilt.x = XMIN
        request.Velocity.PanTilt.y = 0
        self.perform_move(ptz, request, timeout)

    def rtsp_captured_video(self, camera, request):     # RTSP 串流保持與控制
        while True:
            ret, frame = camera.read()
            if not ret:
                print("Camera is disconnected!")
                camera.release()
                return False
            else:
                cv2.namedWindow('onvif camera', cv2.WINDOW_NORMAL)                                          
                cv2.setWindowProperty('onvif camera', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)       # 全螢幕顯示
                cv2.imshow('onvif camera', frame)

            ch = cv2.waitKey(1)
            if ch == ord('w'):
                self.move_up(self.ptz, request)

            elif ch == ord('a'):
                self.move_left(self.ptz, request)

            elif ch == ord('s'):
                self.move_down(self.ptz, request)

            elif ch == ord('d'):
                self.move_right(self.ptz, request)

            if ch == 27 or ch == ord('q') or ch == ord('Q'):
                    break

        return True


if __name__ == '__main__':
    RTSP = r"rtsp://admin:mirdc83300307@192.168.0.237:554/stream1"
    check_finish = True
    while check_finish:
        try:
            OnvifControl = Onvif_control('192.168.0.237', 2020, 'admin', 'mirdc83300307')
            request = OnvifControl.continuous_move()

            while True:
                camera = cv2.VideoCapture(RTSP)
                if camera.isOpened():
                    print('Camera is connected')
                    #call function
                    response = OnvifControl.rtsp_captured_video(camera, request)
                    if response == False:
                        time.sleep(0.5)
                        continue
                    else:
                        check_finish = False
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