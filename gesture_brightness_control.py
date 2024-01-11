import numpy as np
from screen_brightness_control import set_brightness
from screen_brightness_control import get_brightness
from math import hypot




class GestureBrightnessControl():
    def __init__(self):
        # self.hand_detector = ht.HandDetector()
        self.old_brightness = get_brightness()[0]



    def activate_brightness_control(self,capture,hand_detector):

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
            new_brightness = int(np.interp(distance,[20,190],[0,100]))


            # Adjusting the sensitivity
            if abs(self.old_brightness-new_brightness) > 2:
                set_brightness(new_brightness)
                self.old_brightness = new_brightness

            # Once the fingers are closed, make the circle red
            if distance <= 25:
                cv.circle(capture, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (0, 0, 255), cv.FILLED)  # Change the colour of the circle to give it a button effect

            # Else, keep it pink
            else:
                cv.circle(capture, ((x1 + x2) // 2, (y1 + y2) // 2), 10, (255, 0, 255), cv.FILLED)



if __name__ == "__main__":
    from time import time as t
    from handTracking import *

    hand_tracker = HandDetector()
    brightness_control = GestureBrightnessControl()
    cam = cv.VideoCapture(0)

    previous_time = 0
    while True:
        conf, capture = cam.read()
        brightness_control.activate_brightness_control(capture,hand_tracker)
        print("The current brightness",get_brightness()[0])
        cv.imshow("Camera",capture)

        # Find the FPS
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