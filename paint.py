import cv2
import mediapipe as mp
import numpy as np

cap = cv2.VideoCapture(0)

mphands = mp.solutions.hands
hands = mphands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)

painting = None

while True:
    _, frame = cap.read()
    h,w,_ = frame.shape
    frame = cv2.flip(frame,1)

    if painting is None:
        painting = np.zeros_like(frame)

    imageRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(imageRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            index = handLms.landmark[8]
            x, y = int(index.x * w), int(index.y * h)

            cv2.circle(painting,(x,y),1,(255,0,0),-1)
            cv2.circle(frame,(x,y),15,(255,0,0),-1)

    cv2.imshow("Painting", painting)
    cv2.imshow("Camera",frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.imwrite("painting.png",painting)
        break

cap.release()
cv2.destroyAllWindows()