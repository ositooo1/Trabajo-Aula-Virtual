from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import json
import os

app = Flask(__name__)
app.secret_key = 'aula-virtual-secret'

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_data(name):
    path = os.path.join(DATA_DIR, f'{name}.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_data(name, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f'{name}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/students')
def students():
    return render_template('students.html')

@app.route('/content')
def content():
    return render_template('content.html')

@app.route('/evaluations')
def evaluations():
    return render_template('evaluations.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    users = load_data('users')
    for u in users:
        if u['email'] == data.get('email') and u['password'] == data.get('password'):
            return jsonify({'token': 'tok_' + u['email'], 'user': {'id': u['id'], 'username': u['username'], 'role': u['role']}})
    return jsonify({'message': 'Email o contrasena incorrectos'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json()
    users = load_data('users')
    for u in users:
        if u['email'] == data.get('email'):
            return jsonify({'message': 'El email ya esta registrado'}), 400
    new_id = max([u['id'] for u in users], default=0) + 1
    users.append({
        'id': new_id,
        'username': data.get('username', ''),
        'email': data.get('email', ''),
        'password': data.get('password', ''),
        'role': data.get('role', 'estudiante')
    })
    save_data('users', users)
    return jsonify({'message': 'Registro exitoso'}), 201

@app.route('/api/courses', methods=['GET', 'POST'])
def api_courses():
    if request.method == 'GET':
        return jsonify({'courses': load_data('courses')})
    data = request.get_json()
    courses = load_data('courses')
    new_id = max([c['id'] for c in courses], default=0) + 1
    data['id'] = new_id
    data['status'] = data.get('status', 'active')
    courses.append(data)
    save_data('courses', courses)
    return jsonify(data), 201

@app.route('/api/courses/<int:cid>', methods=['PUT', 'DELETE'])
def api_course(cid):
    courses = load_data('courses')
    if request.method == 'DELETE':
        courses = [c for c in courses if c['id'] != cid]
        save_data('courses', courses)
        return jsonify({'message': 'Eliminado'})
    data = request.get_json()
    for c in courses:
        if c['id'] == cid:
            c.update(data)
            save_data('courses', courses)
            return jsonify(c)
    return jsonify({'message': 'No encontrado'}), 404

@app.route('/api/students', methods=['GET', 'POST'])
def api_students():
    if request.method == 'GET':
        return jsonify({'students': load_data('students')})
    data = request.get_json()
    students = load_data('students')
    new_id = max([s['id'] for s in students], default=0) + 1
    data['id'] = new_id
    students.append(data)
    save_data('students', students)
    return jsonify(data), 201

@app.route('/api/students/<int:sid>', methods=['PUT', 'DELETE'])
def api_student(sid):
    students = load_data('students')
    if request.method == 'DELETE':
        students = [s for s in students if s['id'] != sid]
        save_data('students', students)
        return jsonify({'message': 'Eliminado'})
    data = request.get_json()
    for s in students:
        if s['id'] == sid:
            s.update(data)
            save_data('students', students)
            return jsonify(s)
    return jsonify({'message': 'No encontrado'}), 404

@app.route('/api/content', methods=['GET', 'POST'])
def api_content():
    if request.method == 'GET':
        return jsonify({'contents': load_data('content')})
    data = request.get_json()
    contents = load_data('content')
    new_id = max([c['id'] for c in contents], default=0) + 1
    data['id'] = new_id
    contents.append(data)
    save_data('content', contents)
    return jsonify(data), 201

@app.route('/api/content/<int:cid>', methods=['PUT', 'DELETE'])
def api_content_item(cid):
    contents = load_data('content')
    if request.method == 'DELETE':
        contents = [c for c in contents if c['id'] != cid]
        save_data('content', contents)
        return jsonify({'message': 'Eliminado'})
    data = request.get_json()
    for c in contents:
        if c['id'] == cid:
            c.update(data)
            save_data('content', contents)
            return jsonify(c)
    return jsonify({'message': 'No encontrado'}), 404

@app.route('/api/evaluations', methods=['GET', 'POST'])
def api_evaluations():
    if request.method == 'GET':
        return jsonify({'evaluations': load_data('evaluations')})
    data = request.get_json()
    evaluations = load_data('evaluations')
    new_id = max([e['id'] for e in evaluations], default=0) + 1
    data['id'] = new_id
    evaluations.append(data)
    save_data('evaluations', evaluations)
    return jsonify(data), 201

@app.route('/api/evaluations/<int:eid>', methods=['PUT', 'DELETE'])
def api_evaluation(eid):
    evaluations = load_data('evaluations')
    if request.method == 'DELETE':
        evaluations = [e for e in evaluations if e['id'] != eid]
        save_data('evaluations', evaluations)
        return jsonify({'message': 'Eliminado'})
    data = request.get_json()
    for e in evaluations:
        if e['id'] == eid:
            e.update(data)
            save_data('evaluations', evaluations)
            return jsonify(e)
    return jsonify({'message': 'No encontrado'}), 404

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    for name in ['users', 'courses', 'students', 'content', 'evaluations']:
        if not os.path.exists(os.path.join(DATA_DIR, f'{name}.json')):
            save_data(name, [])
    app.run(debug=True)
