import numpy as np
import cv2 as cv
from math import hypot
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


class GestureVolumeControl():
    def __init__(self):

        # self.hand_detector = ht.HandDetector()
        self.old_vol = 0
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)

        self.volume = self.interface.QueryInterface(IAudioEndpointVolume)
        # volume.GetMute()
        # volume.GetMasterVolumeLevel()

        self.volRange = self.volume.GetVolumeRange()
        # volume.SetMasterVolumeLevel(-20.0, None)
        self.minVol = self.volRange[0]
        self.maxVol = self.volRange[1]




    def activate_volume_control(self,capture,hand_detector):
        """
        Activates the hand detection and volume control feature.
        :return:
        """
        hand_detector.find_hands(capture,find_2_closest=False)
        landmark_list = hand_detector.find_position(capture,0,draw=False)

        if len(landmark_list) != 0:

            # Landmark 8 -> thumb, landmark 4 -> index finger
            x1,y1, = landmark_list[4][2], landmark_list[4][3]
            x2,y2 = landmark_list[8][2], landmark_list[8][3]

            # Draw circles on the tips of the index and thumb
            cv.circle(capture,(x1,y1),10,(255,0,255),cv.FILLED) # Index
            cv.circle(capture,(x2,y2),10,(255,0,255),cv.FILLED) # Thumb
            cv.line(capture,(x1,y1),(x2,y2),(255,0,255),4,0)


            # Find the distance between the index and the thumb tips
            distance = hypot((x2-x1),(y2-y1)) # Min 20, Max 200

            # Linearly interpolate the distance and convert it to volume
            new_vol = int(np.interp(distance,[20,200],[-65,0]))

            # Adjusting the sensitivity
            if abs(self.old_vol-new_vol) > 2:
                self.volume.SetMasterVolumeLevel(new_vol, None)
                self.old_vol = new_vol

            # Once the fingers are closed, make the circle red
            if distance <= 25:
                cv.circle(capture, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (0, 0, 255), cv.FILLED)  # Change the colour of the circle to give it a button effect

            # Else, keep it pink
            else:
                cv.circle(capture, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (255, 0, 255), cv.FILLED)  # Index


    def get_current_vol(self):
        current_vol = int(np.interp(self.volume.GetMasterVolumeLevel(), [-65, 0], [0, 100]))
        return current_vol






# Driver test code
if __name__ == "__main__":
    from time import time as t
    from handTracking import *

    hand_tracker = HandDetector()
    volume_gesture_control = GestureVolumeControl()

    cam = cv.VideoCapture(0)

    previous_time = 0


    while True:
        conf, capture = cam.read()
        volume_gesture_control.activate_volume_control(capture,hand_tracker)
        # print("Current volume:",volume_gesture_control.get_current_vol())
        cv.imshow("Camera",capture)
        current_time = t()
        fps = int(1 / (current_time - previous_time))
        previous_time = current_time
        cv.putText(capture, f"{fps} FPS", (capture.shape[1] // 12, capture.shape[0] // 12), cv.FONT_HERSHEY_SIMPLEX, 1,
                   (0, 255, 0), 2)
        cv.imshow("Camera", capture)
        if cv.waitKey(10) != -1:
            break

    cam.release()
    cv.destroyAllWindows()