import flask
import os
import sys
import argparse
import time
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtQml import *
from qml.UnicornUI import *
from internal import *
from werkzeug.serving import WSGIRequestHandler

app = flask.Flask(__name__)

def make_absolute(path) -> str:
    expanded_path = os.path.expanduser(path)
    expanded_path = str(os.path.abspath(expanded_path))
    return expanded_path

def generate_projname(src:str) -> str:
    folder = os.path.basename(src).strip()
    return f"{folder}_{datetime.now().strftime('%Y.%m.%d.%f')}"

def load_env():
    default_path: str = "~/utool_data"
    GloabalContext.app_base = os.environ.get("UTOOL_BASE_PATH") or default_path

def load_appconfig():
    if not GloabalContext.app_base:
        raise ValueError("UTOOL_BASE_PATH not set in environment") 
    cfg_name = f"{GloabalContext.app_base}/config.yaml"
    if not os.path.isfile(cfg_name):
        raise ValueError("Config file not found")  
    GloabalContext.config = ConfigManager(config_path=cfg_name)
    GloabalContext.config.load()

def init_project(src_path:str):
    print(f"init project {src_path}")
    GloabalContext.current_project = Project()
    name = GloabalContext.current_project.project_from_src(src_path)
    if not name:
        # create project
        prjname = generate_projname(src_path)
        print(f"new project {prjname}")
        GloabalContext.current_project.make_project(prjname, src_path)
        return prjname
    GloabalContext.current_project.load_project(name)
    GloabalContext.ui_project_handler = ProjectQObject(GloabalContext.current_project)
    return name

def restored_exit(code, folder):
    os.chdir(folder)
    sys.exit(code)


class TimedRequestHandler(WSGIRequestHandler):
    def handle(self):
        self.start_time = time.time()
        return super().handle()
    
    def log_request(self, code, size=None):
        duration = time.time() - self.start_time
        message = f'{self.requestline} {code} {duration:.3f}s'
        self.log('info', message)

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
def get_summary():
    if GloabalContext.current_project and GloabalContext.current_project.in_project():
        return flask.jsonify(GloabalContext.current_project.to_dict())
    return flask.jsonify(Project.to_dict_placeholder)

@app.route('/api/v1/console')
def get_console():
    msg = GloabalContext.ui_console_controller.text
    response = flask.make_response(msg)
    response.headers['Content-Type'] = 'text/plain'
    return response

@app.route('/api/v1/act')
def execute_action():
    act = flask.request.args.get('act')
    
    if not act or act not in ['run_ctags']:
        return flask.abort(400, "Invalid or missing action parameter")
        
    if not (GloabalContext.current_project and GloabalContext.current_project.in_project()):
        return flask.abort(500, "No project initialized")

    success = GloabalContext.current_project.reindex()
    if success:
        return flask.jsonify({'status': 'success', 
                                'message': 'CTags update started successfully'})
    else:
        return flask.abort(500, "Failed to start CTags update")


if __name__ == '__main__':
    load_env()
    load_appconfig()
    parser = argparse.ArgumentParser(description='Unicorn Tool')
    parser.add_argument('source_path', 
                       type=str, 
                       default=os.getcwd(),
                       help='Path to source directory (optional)',
                       nargs='?')
    args =  parser.parse_args()
    current_dir = os.getcwd()
    project_src = args.source_path.strip().replace('\\', '/')
    project_src = make_absolute(project_src)
    print(f"run source {project_src}")
    started_with_src = bool(project_src)
    if project_src and not os.path.isdir(project_src):
        print(f"Source path '{project_src}' not found!")
        restored_exit(-1, current_dir)

    os.chdir(GloabalContext.app_base)

    GloabalContext.qt_env = False
    GloabalContext.ui_skin = None
    GloabalContext.ui_globals = None
    GloabalContext.tab_controller = None
    GloabalContext.ui_console_controller = ConsoleController()
    prjname = init_project(project_src)
    print(f"run project {prjname}")
    webui_host = os.getenv('UTOOL_HOST', '127.0.0.1')
    webui_port = int(os.getenv('UTOOL_PORT', '5050'))
    app.run(host=webui_host,
            port=webui_port,
            debug=False,
            request_handler=TimedRequestHandler)

    restored_exit(0, current_dir)