from flask import Flask, render_template, request
from PIL import Image, ImageDraw, ImageFont
import os
import io

import cv2

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
#face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

v = 20

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def textsize(text, font):
    im = Image.new(mode="P", size=(0, 0))
    draw = ImageDraw.Draw(im)
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    return width, height

def mosaic(photo_path):
    img = cv2.imread(photo_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        #cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y : y + h, x : x + w]
        roi_color = img[y : y + h, x : x + w]

        roi = cv2.resize(roi_color, (w // v, h // v))
        roi = cv2.resize(roi, (w, h), interpolation=cv2.INTER_AREA)
        img[y:y+h, x:x+w] = roi

    #img = Image.open(photo_path)
    cv2.imwrite(photo_path,img)

# def watermark_photo(photo_path):
#     img = Image.open(photo_path)
#     draw = ImageDraw.Draw(img)
#     font = ImageFont.load_default()

    # watermark_text = "Your Watermark Here"
    # text_width, text_height = textsize(watermark_text, font=font)

    # x = img.width - text_width - 10
    # y = img.height - text_height - 10

    # draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 128))
    # img.save(photo_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'photo' not in request.files:
        return 'No file part'

    file = request.files['photo']

    if file.filename == '':
        return 'No selected file'

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        #watermark_photo(filename)
        #return 'File uploaded and watermarked successfully!'

        mosaic(filename)
        return 'File uploaded and mosaiced successfully!'

    return 'Invalid file format'

if __name__ == '__main__':
    app.run(debug=True)