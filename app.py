from flask import Flask, render_template, request, jsonify
from keras.models import load_model
import numpy as np
from PIL import Image
from tensorflow.keras.preprocessing import image
from tensorflow.keras.utils import get_file
from back_end import Mysql,GCStorage
import os
import io
from google.cloud import storage


model_kubis = load_model("model_kubis.h5", compile=False)
model_bayam = load_model("model_bayam.h5", compile=False)
model_kangkung = load_model("model_kangkung.h5", compile=False)

app = Flask(__name__)

mysql = Mysql("localhost","root","12345678","SegarinDatabase")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'project_segarin.json'

gcs = GCStorage(storage.Client())
bucket_name = "segarin_bucket"

@app.route("/")
def home():
    os.system("sudo systemctl start mysql")
    return "<h1>Selamat datang di API segarin, /bayam untuk  cek segar bayam, /kangkung untuk cek segar kangkung, /kubis untuk cek segar kubis </h1>"

@app.route("/kubis")
def kubis():
    os.system("sudo systemctl start mysql")
    return render_template("kubis.html")

@app.route("/bayam")
def bayam():
    os.system("sudo systemctl start mysql")
    return render_template("bayam.html")

@app.route("/kangkung")
def kangkung():
    os.system("sudo systemctl start mysql")
    return render_template("kangkung.html")


@app.route("/getUser",methods=["POST","GET"])
def getUser():
    os.system("sudo systemctl start mysql")
    data = [string[x] for x in request.form.values()]
    return mysql.get_user(data[0],data[1])

@app.route("/getListUser",methods=["GET"])
def getListUser():
    os.system("sudo systemctl start mysql")
    return mysql.get_list_user()
@app.route("/getListFoto",methods=["GET"])
def getListFoto():
    os.system("sudo systemctl start mysql")
    return mysql.get_list_foto()

@app.route("/insertUser",methods=["POST"])
def insertUser():
    os.system("sudo systemctl start mysql")
    data = [string[x] for x in request.form.values()]
    return insert_user(data[0],data[2],data[1])

@app.route("/fotoKubis", methods =["POST"])
def fotoKubis():
    os.system("sudo systemctl start mysql")
    data_file=  request.files['test']
    tipe = data_file.content_type
    img = Image.open(data_file)
    gcs.upload_file(bucket_name,os.path.join("kubis/",str(data_file.filename)),data_file.read(),tipe)
    data = "foto_kubis"
    img.save(data, "JPEG")
    img = image.load_img(data,target_size=(256,256))
    x = image.img_to_array(img)
    x /= 255
    x = np.expand_dims(x,axis = 0)

    images = np.vstack([x])
    classes = model_kubis.predict(images, batch_size=10)
    output_class= np.argmax(classes)
    classname = ['Tidak Segar', 'Segar']
    mysql.insert_foto(1,str(data_file.filename),"kubis/",str(classname[output_class]))
    return ("The predicted class is "+ str(classname[output_class]))

@app.route("/fotoBayam", methods =["POST"])
def fotoBayam():
    os.system("sudo systemctl start mysql")
    data_file=  request.files['test']
    tipe = data_file.content_type
    gcs.upload_file(bucket_name,os.path.join("bayam/",str(data_file.filename)),data_file.read(),tipe)
    img = Image.open(data_file)
    data = "foto_bayam"
    img.save(data, "JPEG")
    img = image.load_img(data,target_size=(128,128))
    x = image.img_to_array(img)
    x /= 255
    x = np.expand_dims(x,axis = 0)

    images = np.vstack([x])
    classes = model_bayam.predict(images, batch_size=10)
    output_class= np.argmax(classes)
    classname = ['Segar', 'Tidak Segar']
    mysql.insert_foto(1,str(data_file.filename),"bayam/",str(classname[output_class]))
    return ("The predicted class is "+ str(classname[output_class]))

@app.route("/fotoKangkung", methods =["POST"])
def fotoKangkung():
    os.system("sudo systemctl start mysql")
    data_file=  request.files['test']
    tipe = data_file.content_type
    gcs.upload_file(bucket_name,os.path.join("kangkung/",str(data_file.filename)),data_file.read(),tipe)
    img = Image.open(data_file)
    data = "foto_kangkung"
    img.save(data, "JPEG")
    img = image.load_img(data,target_size=(256,256))
    x = image.img_to_array(img)
    x /= 255
    x = np.expand_dims(x,axis = 0)

    images = np.vstack([x])
    classes = model_kangkung.predict(images, batch_size=10)
    output_class= np.argmax(classes)
    classname = ['Tidak Segar', 'Segar']
    mysql.insert_foto(1,str(data_file.filename),"kangkung/",str(classname[output_class]))
    return ("The predicted class is "+ str(classname[output_class]))

if __name__ == '__main__':

 # run() method of Flask class runs the application
 # on the local development server.
 app.run(host='0.0.0.0', port=3003)





