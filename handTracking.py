import cv2 as cv
import mediapipe as mp
import time # To check the frame rate


class HandDetector():
    def __init__(self,mode=False,
               maxHands=2,
               detectionConf=0.5,
               trackingConf=0.5):
        self.mode= mode
        self.maxHands = maxHands
        self.detectionConf = detectionConf
        self.trackingConf = trackingConf

        self.mpHands = mp.solutions.hands  # Import the hands modules
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands, min_detection_confidence=self.detectionConf, min_tracking_confidence=self.trackingConf)  # Apply it
        self.mp_draw_hands = mp.solutions.drawing_utils


    def find_hands(self,frame,draw_flag=True,find_2_closest=False):
        frameRGB = cv.cvtColor(frame,cv.COLOR_BGR2RGB) # Change the colour channels because the mediapipe library deals with RGB, not BGR
        self.output = self.hands.process(frameRGB)

        # Check if we have multiple hands
        if (self.output.multi_hand_landmarks):
            # Draw the hands
            for hand in self.output.multi_hand_landmarks:
                if find_2_closest:
                    target_1, target_2, (cord1_x, cord1_y, cord2_x, cord2_y) = self.calculate_2_nearest_points(point_cords=hand.landmark,frame = frameRGB)
                    cv.circle(frame, (cord1_x, cord1_y), 10, (255, 10, 255), cv.FILLED)
                    cv.circle(frame, (cord2_x, cord2_y), 10, (255, 10, 255), cv.FILLED)
                    cv.line(frame, (cord1_x, cord1_y), (cord2_x, cord2_y), (77,238,234), thickness=2)

                # for id,lmd in enumerate(hand.landmark):
                #     height, width, colour_channel = frame.shape # Get the dimensions and colour channel of the frame
                #     center_x, center_y = int(lmd.x*width), int(lmd.y*height) # Find the coordinates of each landmark
                #     print(f"Landmark ID:{id}, X coordinate:{center_x}, Y Coordinate:{center_y}")
                if draw_flag:
                    self.mp_draw_hands.draw_landmarks(frame,hand,self.mpHands.HAND_CONNECTIONS)

        return frame


    def calculate_2_nearest_points(self,point_cords,frame):
        top_cords = [point_cords[4], point_cords[8],point_cords[12],point_cords[16],point_cords[20]]
        current_min = float('inf')
        target_1 = 0
        target_2 = 0
        cord1_x,cord1_y,cord2_x,cord2_y = 0 ,0 , 0, 0
        height, width, colour_channel = frame.shape
        for id,point in enumerate(top_cords):
            center_x, center_y = int(point.x*width) , int(point.y*height)
            for other_id,other_point in enumerate(top_cords):
                if id != other_id:
                    other_center_x, other_center_y = int(other_point.x * width), int(other_point.y * height)
                    diff_x = abs(other_center_x-center_x)
                    diff_y = abs(other_center_y-center_y)
                    diff_sqr = diff_y**2 + diff_x**2
                    if (diff_sqr) <= current_min:
                        target_1 , target_2 = id, other_id
                        current_min = (diff_sqr)
                        cord1_x, cord1_y, cord2_x, cord2_y = center_x, center_y, other_center_x, other_center_y


        return target_1,target_2,(cord1_x, cord1_y, cord2_x, cord2_y )


    def find_position(self,frame,handNo=0,draw= True):

        landmarks = []
        # Check if we have multiple hands
        if (self.output.multi_hand_landmarks):
            these_hands = self.output.multi_hand_landmarks[:handNo+1] # Get an indivisual hand
            for handid ,this_hand in enumerate(these_hands):
                for id,lmd in enumerate(this_hand.landmark):
                    height, width, colour_channel = frame.shape # Get the dimensions and colour channel of the frame
                    center_x, center_y = int(lmd.x*width), int(lmd.y*height) # Find the coordinates of each landmark
                    landmarks.append([handid,id,center_x,center_y])
                    if draw:
                        cv.circle(frame, (center_x, center_y), 7, (255, 0, 255), cv.BORDER_DEFAULT)

        return landmarks


def main():
    capture = cv.VideoCapture(0)

    mpHands = mp.solutions.hands # Import the hands modules
    hands = mpHands.Hands() # Apply it
    mp_draw_hands = mp.solutions.drawing_utils

    # t1 = time.time()
    # n_frames = 1
    current_min = float('inf')
    current_time = 0
    previous_time = 0
    while True:
        flag, frame = capture.read()
        frameRGB = cv.cvtColor(frame,cv.COLOR_BGR2RGB) # Change the colour channels because the mediapipe library deals with RGB, not BGR
        output = hands.process(frameRGB)

        # Check if we have multiple hands
        if (output.multi_hand_landmarks):
            # Draw the hands
            for hand in output.multi_hand_landmarks:
                for id,lmd in enumerate(hand.landmark):
                    height, width, colour_channel = frame.shape
                    center_x, center_y = int(lmd.x*width), int(lmd.y*height)
                    print(f"Landmark ID:{id}, X coordinate:{center_x}, Y Coordinate:{center_y}")
                #     if id == 8 :
                #         cv.circle(frame,(center_x,center_y),25,(255,10,255),cv.FILLED)
                # target_1,target_2,(cord1_x, cord1_y, cord2_x, cord2_y ) = calculate_2_nearest_points(hand.landmark)
                # cv.circle(frame, (cord1_x, cord1_y), 10, (255, 10, 255), cv.FILLED)
                # cv.circle(frame, (cord2_x, cord2_y), 10, (255, 10, 255), cv.FILLED)

                mp_draw_hands.draw_landmarks(frame,hand,mpHands.HAND_CONNECTIONS)

        # n_frames += 1
        # t2 = time.time()
        # dt = t2-t1
        # frames_per_second = int(n_frames/dt)
        current_time = time.time()
        frames_per_second = int(1/(current_time-previous_time))
        previous_time = current_time

        cv.putText(frame,f"{frames_per_second}",(frame.shape[1]//12,frame.shape[0]//12),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        cv.imshow("Hand Tracking",frame)

        key_stroke_wait = cv.waitKey(30) & 0xFF
        if (key_stroke_wait == ord('q')) or (key_stroke_wait == ord('Q')):
            break

    cv.destroyAllWindows()






# Test driver code
if __name__ == "__main__":
    # main()
    capture = cv.VideoCapture(0)
    current_time = 0
    previous_time = 0
    detector = HandDetector()
    while True:
        flag, frame = capture.read()
        frame = detector.find_hands(frame,find_2_closest=True)
        arr_of_landmakrs = detector.find_position(frame,1,draw=False)
        if len(arr_of_landmakrs) != 0:
            print(arr_of_landmakrs)
        current_time = time.time()
        frames_per_second = int(1/(current_time-previous_time))
        previous_time = current_time

        cv.putText(frame,f"{frames_per_second}",(frame.shape[1]//12,frame.shape[0]//12),cv.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
        cv.imshow("Hand Tracking",frame)

        key_stroke_wait = cv.waitKey(30) & 0xFF
        if (key_stroke_wait == ord('q')) or (key_stroke_wait == ord('Q')):
            break