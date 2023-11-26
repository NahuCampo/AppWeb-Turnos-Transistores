from flask import Flask, render_template, request, redirect, url_for, session
import firebase_admin
from firebase_admin import credentials, firestore, auth

app = Flask(__name__)
app.secret_key = 'your_secret_key'
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# Ruta principal
@app.route('/')
def index():
    # Verificar si el usuario está autenticado
    user = session.get('user')
    if user:
        return render_template('index.html', user=user, turnos=turnos)
    else:
        return redirect(url_for('home'))
    
@app.route('/home')
def home():
    return render_template('home.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print("Hola!")
        print(f'Autenticando al usuario con email: {email}')

        user_ref = db.collection('Usuarios').where('mail', '==', email).get()
        for usuario in user_ref:
            contra = usuario.to_dict().get('password')
            if(password == contra):
                print("Contraseña correcta")
                session['user'] = usuario.to_dict().get('mail')
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Credenciales incorrectas')

    return render_template('login.html', error=None)

# Ruta de cierre de sesión
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/turnos')
def turnos():
    user = session.get('user')
    if user:
        # Obtener lista de profesionales y turnos desde Firestore
        users_ref = db.collection('Usuarios').where('mail', '==', user).get()
        for usuario in users_ref:
            turnos = usuario.to_dict().get('turnos')

        dias = []
        profes = []
        horas = []
        if(turnos == None):
            print("No hay turnos")
            return render_template('turnos.html', dias = dias, profesionales = profes, horas = horas, largo = 0, disponibilidad = True)
        for turno in turnos:
            turno_ref = db.collection('Turnos').document(turno).get()
            dias.append(turno_ref.to_dict().get('dia'))
            profId = turno_ref.to_dict().get('profesionalId')
            print(profId)
            nombreProf = db.collection('Profesionales').document(profId).get().to_dict().get('nombre')
            apellidoProf = db.collection('Profesionales').document(profId).get().to_dict().get('apellido')
            profes.append(nombreProf + " " + apellidoProf)
            horas.append(turno_ref.to_dict().get('horaInicio'))
        largo = len(turnos)
        print(turnos)
        return render_template('turnos.html', dias = dias, profesionales = profes, horas = horas, largo = largo, disponibilidad = False)
    else:
        return redirect(url_for('login'))

@app.route('/profesionales')
def profesionales():
 categorias_ref = db.collection('Categoria').get()
 profesNames = {}
 for categoria in categorias_ref:
     nombres = categoria.id
     profesId = categoria.to_dict().get('profesionales')
     profesName = []
     for profeId in profesId:
         nombreProf = db.collection('Profesionales').document(profeId).get().to_dict().get('nombre')
         apellidoProf = db.collection('Profesionales').document(profeId).get().to_dict().get('apellido')
         profesName.append({'id': profeId, 'name': nombreProf + " " + apellidoProf})
     profesNames[nombres] = profesName
 return render_template('profesionales.html', profes = profesNames)

@app.route('/profesional/<id>')
def profesional(id):
    nombreProf = db.collection('Profesionales').document(id).get().to_dict().get('nombre')
    apellido = db.collection('Profesionales').document(id).get().to_dict().get('apellido')
    descripcion = db.collection('Profesionales').document(id).get().to_dict().get('descripcion')

    nombreCompleto = nombreProf + " " + apellido
    return render_template('profesional.html', nombreCompleto = nombreCompleto, descripcion = descripcion)

@app.route('/editar')
def editar():
    user = session.get('user')
    if user:
        # Obtener lista de profesionales y turnos desde Firestore
        users_ref = db.collection('Usuarios').where('mail', '==', user).get()
        
        nombre = users_ref[0].to_dict().get('nombre')
        apellido = users_ref[0].to_dict().get('apellido')
        edad = users_ref[0].to_dict().get('edad')
        genero = users_ref[0].to_dict().get('genero')
        telefono = users_ref[0].to_dict().get('telefono')
        
        return render_template('editar.html', nombre=nombre, apellido=apellido, edad=edad, genero=genero, telefono=telefono)
    else:
        return redirect(url_for('login'))

@app.route('/cambiar_datos', methods=['GET', 'POST'])
def cambiar_datos():
    user = session.get('user')
    # Recibe los datos del formulario
    datos = request.form
    user_ref = db.collection('Usuarios').where('mail', '==', user).get()
    if request.method == 'POST':
        nombre = request.form['nombre']
        if(nombre == ""):
            nombre = user_ref[0].to_dict().get('nombre')
        apellido = request.form['apellido']
        if(apellido == ""):
            apellido = user_ref[0].to_dict().get('apellido')
        edad = request.form['edad']
        if(edad == ""):
            edad = user_ref[0].to_dict().get('edad')
        genero = request.form['genero']
        if(genero == ""):
            genero = user_ref[0].to_dict().get('genero')
        telefono = request.form['telefono']
        if(telefono == ""):
            telefono = user_ref[0].to_dict().get('telefono')
        db.collection('Usuarios').document(user_ref[0].id).update({
                'nombre': nombre,
                'apellido': apellido,
                'edad': edad,
                'genero': genero,
                'telefono': telefono
        })
        return redirect(url_for('editar'))
    
    return render_template('editar.html')


if __name__ == '__main__':
    app.run(debug=True)
