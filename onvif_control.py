from time import sleep
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

        except Exception as e:
            print('erro :',e)
    
    def continuous_move(self):

        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.media_profile.PTZConfiguration.token
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        request = self.ptz.create_type('ContinuousMove')                         # 連續移動模式
        request.ProfileToken = self.media_profile.token

        # self.ptz.Stop({'ProfileToken': self.media_profile.token})
    
        if request.Velocity is None:
            request.Velocity = self.ptz.GetStatus({'ProfileToken': self.media_profile.token}).Position
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

        # self.move_up(self.ptz, request)
        # self.move_down(self.ptz, request)
        # self.move_right(self.ptz, request)
        # self.move_left(self.ptz, request)
        return request


    def image_back(self, request):
        import cv2 
        # import threading
        import time

        RTSP = r"rtsp://admin:mirdc83300307@192.168.0.115:554/stream1"
        RTSP = r"rtsp://admin:mirdc83300307@192.168.0.115:554/stream2"

        cap = cv2.VideoCapture(RTSP)
        
        # t_up = threading.Thread(target = self.move_up(self.ptz, request))
        # t_left = threading.Thread(target = self.move_left(self.ptz, request))
        # t_down = threading.Thread(target = self.move_down(self.ptz, request))
        # t_right = threading.Thread(target = self.move_right(self.ptz, request))


        while True:
            start = time.time()

            ret, frame = cap.read()

            if ret:
                cv2.imshow("frame",frame)
                ch = cv2.waitKey(1)
                if ch == ord('w'):
                    # t_up.start()
                    self.move_up(self.ptz, request)

                elif ch == ord('a'):
                    # t_left.start()
                    self.move_left(self.ptz, request)

                elif ch == ord('s'):
                    # t_down.start()
                    self.move_down(self.ptz, request)

                elif ch == ord('d'):
                    # t_right.start()
                    self.move_right(self.ptz, request)

                if ch == 27 or ch == ord('q') or ch == ord('Q'):
                    break
            else: 
                break

            end = time.time()
            print("FPS：%f " % (1/(end - start)))

        cv2.destroyAllWindows()
        cap.release()


    def perform_move(self, ptz, request, timeout):
        # Start continuous move
        ptz.ContinuousMove(request)
        # Wait a certain time
        sleep(timeout)
        # Stop continuous move
        ptz.Stop({'ProfileToken': request.ProfileToken})
 
    def move_up(self, ptz, request, timeout=1):
        print('move up...') 
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = YMAX
        self.perform_move(ptz, request, timeout)
    
    def move_down(self, ptz, request, timeout=1):
        print('move down...') 
        request.Velocity.PanTilt.x = 0
        request.Velocity.PanTilt.y = YMIN
        self.perform_move(ptz, request, timeout)
    
    def move_right(self, ptz, request, timeout=1):
        print('move right...') 
        request.Velocity.PanTilt.x = XMAX
        request.Velocity.PanTilt.y = 0
        self.perform_move(ptz, request, timeout)
    
    def move_left(self, ptz, request, timeout=1):
        print('move left...') 
        request.Velocity.PanTilt.x = XMIN
        request.Velocity.PanTilt.y = 0
        self.perform_move(ptz, request, timeout)




if __name__ == '__main__':
    # continuous_move()
    Onvif_control = Onvif_control('192.168.0.115', 2020, 'admin', 'mirdc83300307')
    request = Onvif_control.continuous_move()
    Onvif_control.image_back(request)

    # import threading
    # import time

    # # 建立一個子執行緒
    # t = threading.Thread(target = Onvif_control.continuous_move())

    # # 執行該子執行緒
    # t.start()

    # # 主執行緒繼續執行自己的工作
    # Onvif_control.content_cam()

    # # 等待 t 這個子執行緒結束
    # t.join()

    # print("Done.")