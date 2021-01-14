import json
import os
import traceback

import face_recognition
import pickle
import cv2

from pytube import YouTube

cascPathface = "haarcascade_frontalface_alt2.xml"
faceCascade = cv2.CascadeClassifier(cascPathface)
data = pickle.loads(open('face_enc', "rb").read())

saved_data = {}
data_name = "data.json"
try:
    with open(data_name) as f:
        saved_data=json.load(f)
except:
    pass

def analyse(url):
    try:
        yt = YouTube(url)
        video_name = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
        all_names = {}
        if video_name in saved_data:
            return saved_data[video_name]
        else:
            video_capture = cv2.VideoCapture(video_name)
            width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
            length = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            out = cv2.VideoWriter('out2.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (width, height))
            for j in range(0,length):
                # grab the frame from the threaded video stream
                try:
                    ret, frame = video_capture.read()
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = faceCascade.detectMultiScale(gray,
                                                         scaleFactor=1.1,
                                                         minNeighbors=5,
                                                         minSize=(60, 60),
                                                         flags=cv2.CASCADE_SCALE_IMAGE)

                    # convert the input frame from BGR to RGB
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # the facial embeddings for face in input
                    encodings = face_recognition.face_encodings(rgb)
                    names = []
                    # loop over the facial embeddings incase
                    for encoding in encodings:
                        # Compare encodings with encodings in data["encodings"]
                        matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.6)
                        # set name =inknown if no encoding matches
                        name = "Unknown"
                        # check to see if we have found a match
                        if True in matches:
                            # Find positions at which we get True and store them
                            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                            counts = {}
                            # loop over the matched indexes and maintain a count for
                            # each recognized face face
                            for i in matchedIdxs:
                                name = data["names"][i]
                                # increase count for the name we got
                                counts[name] = counts.get(name, 0) + 1
                            # set name which has highest count
                            name = max(counts, key=counts.get)

                        # update the list of names
                        names.append(name)

                        # loop over the recognized faces
                        for ((x, y, w, h), name) in zip(faces, names):
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(frame, name, (x, y), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.75, (0, 255, 0), 2)
                        out.write(frame)
                    for name in names:
                        all_names[name]=1

                    print(f"{j / length * 100}/100 {j}/{length}")
                except cv2.error:
                    print("cv2 error")

            video_capture.release()
            out.release()
            cv2.destroyAllWindows()
            saved_data[video_name]=list(all_names.keys())
            with open(data_name,"w") as f:
                f.write(json.dumps(saved_data))
            return list(all_names.keys())
    except :
        traceback.print_exc()
        return ["Unknown"]

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/analyze', methods=['POST', 'GET'])
def recognise():
    if request.method == 'POST':
        url = request.form['url'],
    else:
        # get method
        url = request.args['url']

    response=jsonify({"people": analyse(url)})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

app.run()