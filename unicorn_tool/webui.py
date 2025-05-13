import flask
import os


app = flask.Flask(__name__)

@app.route('/<path:filename>')
def static_files(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(script_dir, 'webui_static')
    requested_file = os.path.abspath(os.path.join(static_dir, filename))
    if not requested_file.startswith(static_dir):
        flask.abort(403)
    if not os.path.exists(requested_file):
        flask.abort(404)
    return flask.send_from_directory(static_dir, filename)

@app.route('/')
def root():
    return flask.redirect('/index.html', code=302, Response=None)

@app.route('/api/v1/project')
def api_home():
    data = {
        "project_name": "TEST PROJECT",
        "age": 30,
        "city": "New York"
    }
    return flask.jsonify(data)

    return "Hello, World!"

# Запускаем приложение
if __name__ == '__main__':
    webui_host = os.getenv('UTOOL_HOST', '127.0.0.1')
    webui_port = int(os.getenv('UTOOL_PORT', '5050'))
    app.run(host=webui_host, port=webui_port, debug=True)