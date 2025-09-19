from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

ANDROID_IMG = os.path.abspath('backend/android-x86.qcow2')
ANDROID_VM_PROC = None

def start_android_vm():
    global ANDROID_VM_PROC
    if ANDROID_VM_PROC is not None:
        return False
    cmd = [
        'qemu-system-x86_64',
        '-m', '2048',
        '-enable-kvm',
        '-smp', 'cores=2',
        '-hda', ANDROID_IMG,
        '-net', 'nic',
        '-net', 'user,hostfwd=tcp::5555-:5555',
        '-vnc', ':0'
    ]
    ANDROID_VM_PROC = subprocess.Popen(cmd)
    return True

def stop_android_vm():
    global ANDROID_VM_PROC
    if ANDROID_VM_PROC is not None:
        ANDROID_VM_PROC.terminate()
        ANDROID_VM_PROC.wait()
        ANDROID_VM_PROC = None
        return True
    return False

@app.route('/api/start', methods=['POST'])
def api_start():
    if start_android_vm():
        return jsonify({'status': 'starting'})
    else:
        return jsonify({'error': 'VM already running'}), 400

@app.route('/api/stop', methods=['POST'])
def api_stop():
    if stop_android_vm():
        return jsonify({'status': 'stopped'})
    else:
        return jsonify({'error': 'No VM running'}), 400

@app.route('/api/apk', methods=['POST'])
def api_apk():
    if 'apk' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    apk = request.files['apk']
    apk_path = os.path.join('/tmp', apk.filename)
    apk.save(apk_path)
    # Install the APK via adb
    install_cmd = f"adb connect localhost:5555 && adb -s localhost:5555 install '{apk_path}'"
    result = subprocess.run(install_cmd, shell=True, capture_output=True, text=True)
    os.remove(apk_path)
    if result.returncode == 0:
        return jsonify({'output': result.stdout})
    else:
        return jsonify({'error': result.stderr}), 500

@app.route('/api/adb', methods=['POST'])
def api_adb():
    cmd = request.json.get('command')
    if not cmd:
        return jsonify({'error': 'No command provided'}), 400
    adb_cmd = f"adb connect localhost:5555 && adb -s localhost:5555 {cmd}"
    result = subprocess.run(adb_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        return jsonify({'output': result.stdout})
    else:
        return jsonify({'error': result.stderr}), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    return jsonify({'running': ANDROID_VM_PROC is not None})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
