from flask import Flask, flash, request, redirect, url_for, send_from_directory, render_template, send_file, jsonify
from lxml import etree
from io import StringIO
import webbrowser
from subprocess import check_output
import subprocess
from werkzeug.utils import secure_filename
import json
import xmltodict
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static'


app = Flask(__name__)
app.config['SECRET_KEY'] = "test"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route('/')
def index():
    return render_template('index.html')


@app.route("/dtd")
def dtd():
    return render_template("dtd.html")



# fichiers pour la validation par dtd extern
@app.route('/indtdfile', methods=['POST'])
def indtdfile():
    f1 = request.files['file1']
    f2 = request.files['file2']
    f1.save(f1.filename)
    f2.save(f2.filename)
    dtd = etree.DTD(f1.filename)
    tree = etree.parse(f2.filename)
    os.remove(f1.filename)
    os.remove(f2.filename)
    if (dtd.validate(tree)):
        return jsonify(result=True)
    else:
        return jsonify(result=False)


# fichiers pour la validation par xmlschema
@app.route('/xs', methods=['GET', 'POST'])
def xs():
    if request.method == 'POST':
        fileXML = request.files['fileXML']
        fileXSD = request.files['fileXSD']

        xml_file = etree.parse(fileXML)
        xsd_validator = etree.XMLSchema(file=fileXSD)

        is_valid = xsd_validator.validate(xml_file)

        if (is_valid):
            return render_template('xs.html', res="Le document est valide")
        else:
            return render_template('xs.html', res="Le document est invalide")

    return render_template('xs.html')



# convertir de dtd vers xsd
@app.route('/DTDversXSD', methods=['GET', 'POST'])
def DTDverXSD():
    if request.method == "POST":

            fileDTD = request.files['fileDTD']
            filename = secure_filename(fileDTD.filename)
            fileDTD.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            dtd_file = "static/" + filename

            _, file_extension = os.path.splitext(fileDTD.filename)

            if file_extension == ".dtd":
                try:
                    pipe = check_output(["perl", "dtd2xsd.pl", dtd_file], stdin=subprocess.PIPE).decode("UTF-8")
                    # ss = str(pipe.replace("b\"",""))
                    print(pipe)
                    f = open("xsd.xsd", "w")
                    f.write(pipe)
                    f.close()

                    return send_file("xsd.xsd", as_attachment=True)

                except:
                    print('error')
            else:
                error = "Your file is not a .dtd File, Retry again !"
                return render_template('DTDversXSD.html', error=error)

    return render_template('DTDversXSD.html')

   # convertir en json
@app.route('/json', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

        file = request.files['file']


        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            with open("static/"+file.filename) as xml_file:
                data_dict = xmltodict.parse(xml_file.read())
                json_data = json.dumps(data_dict)
                f = open("json.json", "a")
                f.write(json_data)
                f.close()
                return send_file("json.json",as_attachment=True)
                    # return redirect(url_for('download_file', name="yourJson.json"))
        else:
           print('notAllowedFile')
    return render_template('json.html')

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

if __name__ == '__main__':
    app.debug = True
    app.run()