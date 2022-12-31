import cv2
video = cv2.VideoCapture('tree2.mp4')

fps = video.get(cv2.CAP_PROP_FPS)

list = []

for i in range(50):
    currentframe = 5*i+2
    frameId = int(fps*currentframe)
    
    video.set(cv2.CAP_PROP_POS_FRAMES, frameId)

    ret, frame = video.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    radius = 11

    gray = cv2.GaussianBlur(gray, (radius,radius), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)
    cv2.circle(frame, maxLoc, radius, (255, 0, 0), 2)
    
    print(f'Location: {maxLoc}, Index: {i}')
    list.append(maxLoc)

    cv2.imshow('frame', frame); cv2.waitKey(0)
print(list)
