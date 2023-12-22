from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import subprocess
from PIL import Image
import cv2
import numpy as np
from PIL import Image
from daltonlens import simulate
from colourblind import process_video
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        original_filename = secure_filename(file.filename)
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        
        file.save(file_path)
        output_video_path_contrast_filename = 'output_video_path_contrast' + original_filename
        output_video_path_contrast= os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], output_video_path_contrast_filename )
        # Run Python script on the uploaded image
        input_video_path=file_path
        output_video_path_protan_filename = 'output_video_path_protan' + original_filename
        output_video_path_protan= os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], output_video_path_protan_filename )
        process_video(input_video_path, output_video_path_contrast, output_video_path_protan, contrast_factor=1.5, severity=0.8)
        
        # Redirect to another webpage with the relative result
        return redirect(url_for('result_page'))

    return render_template('index.html', form=form)

@app.route('/result')
def result_page():
    static_folder = os.path.join(app.root_path, 'static','files')

    videos = [video for video in os.listdir(static_folder)if video.endswith('.mp4')]
    titles=['Protanomlised Video','Original Video','Higher Contrast Video']
    # Render the HTML template with the list of video files
    video_data = zip(videos, titles)
    return render_template('result.html', videos=videos,titles=titles)

if __name__ == '__main__':
    app.run(debug=True)
