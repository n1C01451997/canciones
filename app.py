from flask import Flask,render_template,redirect,request,url_for,flash,session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import base64

#creamos una instancia de la clase flask
app = Flask(__name__)
app.secret_key='728203215'

#definir ruta
db= mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="agenda2024"
    )
#c
cursor = db.cursor()

#incapacidad medica 

@app.route('/password/<contraencrip>')

def encriptarcontra(contraencrip):
    # generar un hash de la contraseña
    #encriptar = bcrypt.hashpw(contraencrip.encode("utf-8"),bcrypt.gensalt())
   encriptar = generate_password_hash(contraencrip)
   valor = check_password_hash(encriptar,contraencrip)
  # return "Encriptado:{0} | coincide:{1}".format(encriptar,valor)
   return valor

#iniciar sesion
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        #verificar las credenciales del usuario
        username = request.form.get('txtusuario')
        #son los mismos campos de la variable
        password = request.form.get('txtcontrasena')
        cursor = db.cursor()
        cursor.execute("SELECT usuario,contraseña,rol FROM personas WHERE  usuario = %s",(username,))
        resultado = cursor.fetchone()

        #el uno lo definimos con el que esta en la linea 35
        if resultado and check_password_hash(resultado[1],password):
            session['usuario']= username
            session['rol'] = resultado [2]

            if resultado[2] == 'administrador':
                return redirect(url_for('lista'))
            else:
                return redirect(url_for('mostrarcanciones'))
        else:
           print("credenciales invalidas")
           return render_template('login.html')

    return render_template('login.html')

#fin incapacidad medica

#ruta cierrede sesion

@app.route('/logout')
def logout():
    #eliminar el usuario de la sesion en otras palabras cerrar sesion 
    session.pop('usuario',None)
    print('cerro sesion')
    return redirect(url_for('login'))


#definir ruta
@app.route('/lista')
def lista():#item
    cursor = db.cursor()#permitir ejecutar
    cursor.execute('select * FROM personas')
    usuario = cursor.fetchall()#

    return render_template('index.html',personas=usuario)#esta renderizando el index.html, y le esta enviando argumentos osea "persosnas" y que la convierta en una variable 
#desde aqui empece a adelantarme ----------
@app.route('/Registrar', methods=['GET','POST'])
def registrar_usuario():
    if request.method == 'POST':
        nombres = request.form.get('nombre')
        apellidos = request.form.get('apellido')
        correo = request.form.get('email')
        direccion  = request.form.get('direccion')
        telefono = request.form.get('telefono')
        usuario = request.form.get('usuario')
        Contrasenas = request.form.get('contrasena')
        roles = request.form.get('rol')

        if Contrasenas is not None:
            #encriptar contraseña
            print("Valor de Contrasenas:", Contrasenas)
            Contrasenas = generate_password_hash(Contrasenas)

            #verificar usuario y correo si existe en la base de datos 

            cursor = db.cursor()
            cursor.execute(
                "SELECT * FROM personas WHERE usuario = %s or email_persona = %s", (usuario,correo))
            existing_user = cursor.fetchone()

            if existing_user:
                #flash('El usuario o correo ya está registrado. Por favor, use otro usuario.', 'error')
                print('El usuario o correo ya está registrado. Por favor, use otro usuario.', 'error')
                return render_template('Registrar.html')
        
            #insertar datos ala tabla personas

            cursor.execute("INSERT INTO personas(nombre_persona,apellido_persona,email_persona,direccion,telefono,usuario,contraseña,rol)VALUES(%s,%s,%s,%s,%s,%s,%s,%s)",
                  (nombres,apellidos,correo,direccion,telefono,usuario,Contrasenas,roles))
            db.commit()
            #metodo para generar mensajes 
            ##flash('usuario credo correctamente','success')
            print('Usuario creado correctamente. Por favor, inicie sesión.', 'success')

            #en caso de que sea solicitud, redirige a la misma pagina cuando el metodo es POST
            return redirect(url_for('login'))
    
        else:
        # si es metodo get me renderiza el formulario
            print('La contraseña no puede ser None')
            return render_template('Registrar.html')
    
    return render_template('Registrar.html')

@app.route('/editar/<int:id>',methods=['GET','POST'])
def editar_usuario(id):
    cursor =db.cursor()
    if request.method  =='POST':
        nombper = request.form.get('nombreper')
        apelldoper = request.form.get('apellidoper')
        emailpers = request.form.get('emailper')
        direcper = request.form.get('direccionper')
        teleper = request.form.get('telefonoper')
        usuarper = request.form.get('usuarioper')
        passwper = request.form.get('passwordper')
        roles = request.form.get('rol')

        #sentencia para actualizar los datos en la base de datos
        sql = "UPDATE personas SET nombre_persona=%s, apellido_persona=%s, email_persona=%s, direccion=%s, telefono=%s, usuario=%s, contraseña=%s, rol=%s WHERE id_perso=%s"
        cursor.execute(sql, (nombper,apelldoper,emailpers,direcper,teleper,usuarper,passwper, roles ,id))
        db.commit()

        return redirect(url_for('lista'))#redirecciona a una url
    else:
        #obtener los datos de la persona que se va a editar
        cursor.execute('SELECT * FROM personas WHERE id_perso = %s', (id,))
        data = cursor.fetchall() 

        if data:
            return render_template('editar.html',persona=data[0])#redirecciona a html
        else:
            flash ('usuario no encontrado', 'Error ')
            return redirect(url_for('lista'))
@app.route('/eliminar/<int:id>',methods=['GET','POST'])
def eliminar_usuario(id):
    cursor =db.cursor()
    if request.method  =='POST':
        sql = "DELETE FROM personas WHERE id_perso=%s"
        cursor.execute(sql,(id,))
        db.commit()
        return redirect (url_for('lista'))
    else:
        cursor.execute('SELECT * FROM personas WHERE id_perso = %s', (id,))
        data = cursor.fetchall() 

        if data:
            return render_template('eliminar.html',persona=data[0])
        else:
            return ("Metodo Invalido")

        
        





















#hasta aqui -------------------

#definir ruta 2
@app.route('/mostrarcanciones')
def listacanciones():#item
    cursor = db.cursor()#permitir ejecutar
    cursor.execute("SELECT titulo_cancion, nombre_artista_cancion, genero, duracion, precio, Alanzamiento, img FROM canciones")
    usuario1 = cursor.fetchall()#

    #crear lista para almacenar canciones

    if usuario1:
        cancioneslist = []
        for cancion in usuario1:
            #convertir imagen en un formato conocido como base 64
            imagen = base64.b64encode(cancion[6]).decode('utf-8')
            #agregar datos de la cancion a la lista
            cancioneslist.append({
                
                'titulo': cancion[0],
                'artista': cancion[1],
                'genero': cancion[2],
                'precio': cancion[3],
                'duracion': cancion[4],
                'lanzamiento': cancion[5],
                'imagen': imagen
                })


        return render_template('listacanciones.html', canciones=cancioneslist)#esta renderizando el index.html, y le esta enviando argumentos osea "persosnas" y que la convierta en una variable 
    else:
        return print("canciones no encontradas")
    

#Registro canciones 
@app.route('/registrarcancion', methods=['GET','POST'])
def registrar_cancion():
    if request.method == 'POST':

        Titulocan = request.form.get('titulocancion')
        artistacan = request.form.get('Artista')
        generocan = request.form.get('genero')
        duracioncan  = request.form.get('duracion')
        preciocan = request.form.get('precio')
        alanzamientocan = request.form.get('Alanzamiento')
        imagencan = request.files['imgcancion']#se realizan esta linea para obtener la imagen del formulario 
        imagenblob = imagencan.read()#se lee y proyectan los datos de la imagen 

        cursor.execute(
           "SELECT * FROM canciones WHERE titulo_cancion = %s AND nombre_artista_cancion = %s", (Titulocan,artistacan))
        existing_song = cursor.fetchone()

        if existing_song:
           #flash('La cancion de este artista ya está registrada. Por favor, registre otra cancion.', 'error')
           print('La cancion de este artista ya está registrada. Por favor, registre otra cancion.', 'error')
           return render_template('registrarcancion.html')

        #insertar datos ala tabla canciones

        cursor.execute("INSERT INTO canciones (titulo_cancion, nombre_artista_cancion, genero, duracion, precio, Alanzamiento, img) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                      (Titulocan, artistacan, generocan, duracioncan, preciocan, alanzamientocan, imagenblob))
        db.commit()
        #metodo para generar mensajes 
        ##flash('La cancion de este artista ha sido creada correctamente.', 'success')
        print(imagenblob)
        print('La cancion de este artista ha sido creada correctamente.', 'success')
        return redirect(url_for('listacanciones'))
    # si es metodo get me renderiza el formulario
    return render_template('registrarcancion.html')

#actualizar canciones 
@app.route('/actualizarcancion/<int:id>',methods=['GET','POST'])
def actualizar_cancion(id):
    cursor =db.cursor()
    if request.method  =='POST':
        titucan = request.form.get('titulocancion')
        artiscan = request.form.get('Artista')
        genecan = request.form.get('genero')
        duracican = request.form.get('duracion')
        precican = request.form.get('precio')
        fechdelanzcan = request.form.get('Alanzamiento')
        imgcancio = request.form.get('imgcancion')

        #sentencia para actualizar los datos en la base de datos
        sql = "UPDATE canciones SET titulo_cancion=%s, nombre_artista_cancion=%s, genero=%s, duracion=%s, precio=%s, Alanzamiento=%s, img=%s WHERE id_canciones=%s"
        cursor.execute(sql, (titucan,artiscan,genecan,duracican,precican,fechdelanzcan,imgcancio,id))
        db.commit()

        return redirect(url_for('listacanciones'))#redirecciona a una url
    else:
        #obtener los datos de la cancion que se va a actualizar
        cursor.execute('SELECT * FROM canciones WHERE id_canciones = %s', (id,))
        data = cursor.fetchall() 

        if data:
            return render_template('actualizarcancion.html',cancion=data[0])#redirecciona a html
        else:
            flash ('cancion no encontrada', 'Error ')
            return redirect(url_for('listacanciones'))
        

#eliminar canion
@app.route('/eliminarcancion/<int:id>',methods=['GET','POST'])
def eliminarcancion(id):
    cursor =db.cursor()
    if request.method  =='POST':
        sql = "DELETE FROM canciones WHERE id_canciones=%s"
        cursor.execute(sql,(id,))
        db.commit()
        return redirect (url_for('listacanciones'))
    else:
        cursor.execute('SELECT * FROM canciones WHERE id_canciones = %s', (id,))
        data = cursor.fetchall() 

        if data:
            return render_template('eliminarcancion.html',cancion=data[0])
        else:
            return ("Metodo Invalido")
        

#para ejecutar instalacion 

if __name__ == '__main__':
    app.add_url_rule('/',view_func=lista)
    app.run(debug=True,port=5005)

