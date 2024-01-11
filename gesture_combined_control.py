import os

import cv2 as cv
import numpy as np
from screen_brightness_control import set_brightness
from screen_brightness_control import get_brightness
from math import hypot
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import handTracking as ht


class GestureBrightnessAndVolumeControl():

    def __init__(self):
        # self.hand_detector = ht.HandDetector()
        self.cam = cv.VideoCapture(0)
        self.old_brightness = get_brightness()[0]
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




    def find_distance(self,capture,hand_detector):

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


            cord_1 = (x1,y1)
            cord_2 = (x2,y2)
            return distance,cord_1,cord_2




    def volume_control(self, capture, hand_detector):
        data = self.find_distance(capture,hand_detector)

        if data:
            # Unpack the coordinats of the index and thumb fingers
            distance, cord_1, cord_2 = data
            x1 , y1 = cord_1
            x2 , y2 = cord_2
            new_vol = int(np.interp(distance, [20, 190], [-65, 0]))

            # Adjusting the sensitivity
            if abs(self.old_vol - new_vol) > 2:
                self.volume.SetMasterVolumeLevel(new_vol, None)
                self.old_vol = new_vol

            # Once the fingers are closed, make the circle red
            if distance <= 25:
                cv.circle(capture, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (0, 0, 255),
                          cv.FILLED)  # Change the colour of the circle to give it a button effect

            # Else, keep it pink
            else:
                cv.circle(capture, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (255, 0, 255), cv.FILLED)




    def brightness_control(self, capture, hand_detector):
        data = self.find_distance(capture,hand_detector)

        # If there is actual data (i.e there are hands detected and its not a None type)
        if data:
            distance , cord_1, cord_2 = data
            x1, y1 = cord_1
            x2, y2 = cord_2
            new_brightness = int(np.interp(distance, [20, 190], [0, 100]))

            # Adjust the sensitivity
            if abs(self.old_brightness - new_brightness) > 2:
                set_brightness(new_brightness)
                self.old_brightness = new_brightness

            # Once the fingers are closed, make the circle red
            if distance <= 25:
                cv.circle(capture, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (0, 0, 255),
                          cv.FILLED)  # Change the colour of the circle to give it a button effect

            # Else, keep it pink
            else:
                cv.circle(capture, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (255, 0, 255), cv.FILLED)



    def combined_volume_and_brightness(self,capture,hand_detector):
        data = self.find_distance(capture,hand_detector)

        # If there is actual data (i.e there are hands detected and its not a None type)
        if data:
            distance, cord_1, cord_2 = data
            x1, y1 = cord_1
            x2, y2 = cord_2
            new_brightness = int(np.interp(distance, [20, 190], [0, 100]))
            new_vol = int(np.interp(distance, [20, 190], [-65, 0]))

            if abs(self.old_vol - new_vol) > 2:
                self.volume.SetMasterVolumeLevel(new_vol, None)
                self.old_vol = new_vol

            # Adjust the sensitivity
            if abs(self.old_brightness - new_brightness) > 2:
                set_brightness(new_brightness)
                self.old_brightness = new_brightness

            # Once the fingers are closed, make the circle red
            if distance <= 25:
                cv.circle(capture, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (0, 0, 255),
                          cv.FILLED)  # Change the colour of the circle to give it a button effect

            # Else, keep it pink
            else:
                cv.circle(capture, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (255, 0, 255), cv.FILLED)


    def get_current_vol(self):
        current_vol = int(np.interp(self.volume.GetMasterVolumeLevel(), [-65, 0], [0, 100]))
        return current_vol


    def get_current_brightness(self):
        brightness = get_brightness()
        return brightness


    def destroy_all(self):
        # cam.release()
        cv.destroyAllWindows()


    def activate_brightness_change(self):
        Path = r"C:\Users\Acer\Desktop\brightness.txt"
        if os.path.exists(Path):
            with open(Path, 'r') as text:
                stop_flag = int(text.readline().strip('\n'))

        print("Brightness flag:",stop_flag)

        hand_tracker = ht.HandDetector()
        while not stop_flag:
            conf, capture = self.cam.read()
            self.brightness_control(capture, hand_tracker)
            cv.imshow("Camera", capture)
            if os.path.exists(Path):
                with open(Path,'r') as text:
                    reader = text.readline().strip('\n')
                    if reader == '1':
                        break
        if not stop_flag:
            with open(Path, 'w') as text:
                reader = text.write('1')
                self.destroy_all()



    def activate_volume_change(self):
        Path = r"C:\Users\Acer\Desktop\volume.txt"
        if os.path.exists(Path):
            with open(Path, 'r') as text:
                stopflag = int(text.readline().strip('\n'))

        print("Volume flag:",stopflag)

        hand_tracker = ht.HandDetector()
        while not stopflag:
            conf, capture = self.cam.read()
            self.volume_control(capture, hand_tracker)
            cv.imshow("Camera", capture)
            if os.path.exists(Path):
                with open(Path, 'r') as text:
                    reader = text.readline().strip('\n')
                    if reader == '1':
                        break

        if not stopflag:
            with open(Path, 'w') as text:
                reader = int(text.write('1'))
            self.destroy_all()


# Driver test code
if __name__ == "__main__":
    from time import time as t
    from handTracking import *



    # Control = GestureBrightnessAndVolumeControl()
    # Control.activate_brightness_change()
    # cam = cv.VideoCapture(0)
    #
    # previous_time = 0
    # while True:
    #     conf, capture = cam.read()
    #     Control.activate_brightness_change()
    #
    #     print("The current brightness",get_brightness()[0])
    #     cv.imshow("Camera",capture)
    #
    #     # Find the FPS
    #     current_time = t()
    #     fps = int(1 / (current_time - previous_time))
    #     previous_time = current_time
    #     cv.putText(capture, f"{fps} FPS", (capture.shape[1] // 12, capture.shape[0] // 12), cv.FONT_HERSHEY_SIMPLEX, 1,
    #                (0, 255, 0), 2)
    #     cv.imshow("Camera", capture)
    #     if cv.waitKey(10) != -1:
    #         break
    #
    # cam.release()
    # cv.destroyAllWindows()