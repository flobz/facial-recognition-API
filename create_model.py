from imutils import paths
import face_recognition
import pickle
import cv2
import os
from threading import Thread, Lock

imagePaths = list(paths.list_images('images'))
knownEncodings = []
knownNames = []
lock = Lock()

len(imagePaths*2)
# loop over the image paths
def image_reco(imagepaths):
    global knownNames, knownEncodings
    oldname="-1"
    for (i, imagePath) in enumerate(imagepaths):
        # extract the person name from the image path
        name = imagePath.split(os.path.sep)[-2]
        if name!=oldname:
            if knownNames.count(name) < 10:
                print(name)
                # load the input image and convert it from BGR (OpenCV ordering)
                # to dlib ordering (RGB)
                image = cv2.imread(imagePath)
                try:
                    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    # Use Face_recognition to locate faces
                    boxes = face_recognition.face_locations(rgb, model='hog')
                    # compute the facial embedding for the face
                    encodings = face_recognition.face_encodings(rgb, boxes)
                    # loop over the encodings
                    lock.acquire()
                    for encoding in encodings:
                        knownEncodings.append(encoding)
                        knownNames.append(name)
                    lock.release()
                except:
                    print(f"Error {name}")
                print(f"{i / len(imagepaths) * 100}/100")
            else:
                oldname = name


cpu = 8
nbimage = int(len(imagePaths) / cpu)
for x in range(0, cpu):
    if x + 1 == cpu:
        Thread(target=image_reco, args=[imagePaths[x * nbimage:]]).start()
    else:
        Thread(target=image_reco, args=[imagePaths[x * nbimage:(x + 1) * nbimage]]).start()
# save encodings along with their names in dictionary data
len(knownNames)
data = {"encodings": knownEncodings, "names": knownNames}
# use pickle to save data into a file for later use
f = open("face_enc", "wb")
f.write(pickle.dumps(data))
f.close()
