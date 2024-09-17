from flask import Flask, send_file

app = Flask(__name__)

@app.route('/image')

def serve_image():
	return send_file('Plan.jpg', mimetype='image/png')

if __name__== '__main__': 
	app.run(host='0.0.0.0', port=8080)
