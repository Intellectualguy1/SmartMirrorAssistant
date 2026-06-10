from deepface import DeepFace
import cv2

# Load webcam
cap = cv2.VideoCapture(0)

print("Scanning for faces...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        result = DeepFace.find(img_path=frame, db_path="faces", enforce_detection=False)
        if len(result) > 0:
            print("Face recognized!")
            break
    except Exception as e:
        print("Face not detected:", e)

    cv2.imshow("Smart Mirror - Face Scan", frame)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()