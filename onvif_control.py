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

    def perform_move(self, ptz, request, timeout):
        # Start continuous move
        ptz.ContinuousMove(request)
        # Wait a certain time
        time.sleep(timeout)
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

    def image_back(self, request):
        RTSP = r"rtsp://admin:mirdc83300307@192.168.0.237:554/stream1"
        RTSP = r"rtsp://admin:mirdc83300307@192.168.0.237:554/stream2"
        
        cap = cv2.VideoCapture(RTSP)


        while True:
            start = time.time()

            ret, frame = cap.read()

            if ret:
                cv2.imshow("frame",frame)
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
            else: 
                break

            end = time.time()
            print("FPS：%f " % (1/(end - start)))

        cv2.destroyAllWindows()
        cap.release()

    def rtsp_captured_video(self, camera, request):
        while True:
            ret, frame = camera.read()
            if not ret:
                print("Camera is disconnected!")
                camera.release()
                return False
            else:
                cv2.imshow('frame', frame)

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

    Onvif_control = Onvif_control('192.168.0.237', 2020, 'admin', 'mirdc83300307')
    request = Onvif_control.continuous_move()

    while True:
        camera = cv2.VideoCapture(RTSP)
        if camera.isOpened():
            print('Camera is connected')
            #call function
            response = Onvif_control.rtsp_captured_video(camera, request)
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
    