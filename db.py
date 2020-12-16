import sqlite3
from sqlite3 import Error
from flask import current_app, g


def conectar():
    try:
        if 'db' not in g:
            g.db = sqlite3.connect('MinTICstagram.db')
        return g.db
    except Error as e:
        print(e)
        

def desconectar():
    try:
        db = g.pop('db', None)
        if db is not None:
            db.close()
    except Error as e:
        print(e)


def insertar_usuario(nombre, correo, contraseña):
    '''
    Inserta un nuevo usuario a la base de datos, por defecto con la cuenta sin
    activar
    '''
    query = """INSERT INTO Usuarios (nombre_usuario, correo, contraseña, activado)
               VALUES (?, ?, ?, 0);"""
    values = (f"'{nombre}'", f"'{correo}'", f"'{contraseña}'")
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query,values)
        con.commit()
        desconectar()
    except Error as e:
        print(e)


def get_usuario(nombre):
    '''
    Retorna un diccionario que represnta un usuario con las llaves id, nombre,
    correo y contraseña si, None si no se encuentra en la base de datos.
    '''
    query = """SELECT id, nombre_usuario, correo, contraseña 
               FROM Usuarios 
               WHERE nombre_usuario=?;"""
    values = (f"'{nombre}'",)
    keys = ['id', 'nombre', 'correo', 'contraseña']
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        res = cursor.fetchone()
        desconectar()
        return None if res is None else {k:v for k,v in zip(keys, res)}
    except Error as e:
        print(e)

def get_usuario_byID(id_):
    '''
    Retorna un diccionario que represnta un usuario con las llaves id, nombre,
    correo y contraseña si, None si no se encuentra en la base de datos.
    '''
    query = """SELECT id, nombre_usuario, correo, contraseña 
               FROM Usuarios 
               WHERE id=?;"""
    values = (f'{id_}',)
    keys = ['id', 'nombre', 'correo', 'contraseña']
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        res = cursor.fetchone()
        desconectar()
        return None if res is None else {k:v for k,v in zip(keys, res)}
    except Error as e:
        print(e)


def activar_usuario(nombre):
    '''
    Activar la cuenta de un usuario
    '''
    query = "UPDATE Usuarios SET activado=1 WHERE nombre_usuario=?;"
    values = (f"'{nombre}'",)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        con.commit()
        desconectar()
    except Error as e:
        print(e)

def actualizar_contraseña(id_, contraseña):
    '''
    Actualizar la contraseña del usuario identificado con id_ en la base de datos
    '''
    query = "UPDATE Usuarios SET contraseña=? WHERE id=?;"
    values = (f"'{contraseña}'", id_)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        con.commit()
        desconectar()
    except Error as e:
        print(e)

def validar_nuevo_usuario(nombre, correo):
    '''
    Retorna una lista de mensajes indicando si el nombre de usuario o el
    '''
    query = """SELECT nombre_usuario, correo 
               FROM Usuarios 
               WHERE nombre_usuario=? OR correo=?;"""
    values = (f"'{nombre}'", f"'{correo}'")
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        usuarios = cursor.fetchall()
        desconectar()
        msgs = []
        for usuario in usuarios:
            if usuario[0] == nombre: 
                msgs.append("El nombre ya se encuentra registrado")
            if usuario[1] == correo:
                msgs.append("El correo ya se encuentra registrado")
        if len(msgs) == 0:
            msgs.append("OK")
        return msgs        
    except Error as e:
        print(e)


def get_id_usuario(nombre):
    '''
    obtener el id de un usuario por su nombre de usuario
    '''
    query = "SELECT id FROM Usuario WHERE nombre=?;"
    values = (f"'{nombre}'",)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        res = cursor.fetchone()
        desconectar()
        return res[0]
        
    except Error as e:
        print(e)


def get_imagenes(usrId, privada):
    '''
    Consultar lista de imagenes para el usario de id usrId, privada es un
    booleano que indica si se desea consultar las imagenes privadas o publicas.
    Se retorna una lista de diccionarios con las llaves: id, nombre, ruta y
    etiquetas, siendo esta última una lista
    '''
    query = """SELECT id, nombre_imagen, ruta 
               FROM Imagenes 
               WHERE id_usuario=? AND privada=?;"""
    values = (usrId, 1 if privada else 0)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        imagenes = cursor.fetchall()
        desconectar()
        # convertir el resultado a una lista de diccionarios
        keys = ['id', 'nombre', 'ruta']
        imagenes = [{k:v for k,v in zip(keys,img)} for img in imagenes]
        for img in imagenes: 
            img['etiquetas'] = get_etiquetas(img['id'])
            
        return imagenes
    except Error as e:
        print(e)

def get_todas_imagenes(usrId):
    '''
    Consultar lista de imagenes para el usario de id usrId, privada es un
    booleano que indica si se desea consultar las imagenes privadas o publicas.
    Se retorna una lista de diccionarios con las llaves: id, nombre, ruta y
    etiquetas, siendo esta última una lista
    '''
    query = """SELECT id, nombre_imagen, ruta 
               FROM Imagenes 
               WHERE id_usuario=?;"""
    values = (usrId,)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        imagenes = cursor.fetchall()
        desconectar()
        # convertir el resultado a una lista de diccionarios
        keys = ['id', 'nombre', 'ruta']
        imagenes = [{k:v for k,v in zip(keys,img)} for img in imagenes]
        for img in imagenes: 
            img['etiquetas'] = get_etiquetas(img['id'])

        return imagenes
    except Error as e:
        print(e)

def get_guardadas(usrId):
    '''
    Consultar lista de imagenes guardadas para el usario de id usrId.
    Sólo retorna imagenes de otros usuarios a las que se les dio 'me gusta'.
    Se retorna una lista de diccionarios con las llaves: id, nombre, ruta y
    etiquetas, siendo esta última una lista
    '''
    query = """SELECT I.id, I.nombre_imagen, I.ruta 
               FROM Imagenes AS I 
               INNER JOIN MeGusta AS MG ON MG.id_imagen = I.id 
               WHERE MG.id_usuario=?;"""
    values = (usrId,)
    
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        imagenes = cursor.fetchall()
        desconectar()
        # convertir el resultado a una lista de diccionarios
        keys = ['id', 'nombre', 'ruta']
        imagenes = [{k:v for k,v in zip(keys,img)} for img in imagenes]
        for img in imagenes: 
            img['etiquetas'] = get_etiquetas(img['id'])

        return imagenes
    except Error as e:
        print(e)


def get_etiquetas(imgId):
    '''
    Retorna una lista con las etiquetas asociadas a la imagen identificada con
    el id imgId
    '''
    query = """SELECT E.nombre_etiqueta 
               FROM Etiquetas AS E 
               INNER JOIN Imagenes_Etiquetas IE ON IE.id_etiqueta=E.id 
               WHERE IE.id_imagen=?;"""
    values = (imgId,)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        etiquetas = cursor.fetchall()
        desconectar()
        return [e[0] for e in etiquetas]
    except Error as e:
        print(e)


def insertar_etiqueta(nombre_etiqueta):
    '''
    Inserta una etiqueta en la base de datos, si la etiqueta ya se encuentra en
    la base de datos se ignora la inserción 
    '''
    query = """INSERT OR IGNORE 
               INTO Etiquetas (nombre_etiqueta) 
               VALUES (?);"""
    values = (f"'{nombre_etiqueta}'",)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        con.commit()
        desconectar()
    except Error as e:
        print(e)


def get_id_etiqueta(nombre_etiqueta):
    '''
    Obtener el id de una etiqueta dado su nombre. Si no se encuentra en la base
    de datos retorna None
    '''
    query = "SELECT id FROM Etiquetas WHERE nombre_etiqueta=?;"
    values = (f"'{nombre_etiqueta}'",)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        res = cursor.fetchone()
        desconectar()
        return res if res is None else res[0]
        
    except Error as e:
        print(e)


def insertar_guardadas(id_usuario,id_imagen):
    '''
    Guarda en la base de datos que un usuario le dio 'me gusta' a una imagen
    de otro usuario
    '''
    query = "INSERT INTO MeGusta (id_usuario, id_imagen) VALUES(?,?);"
    values = (id_usuario, id_imagen)
    try:
        con = conectar()
        cursorObj= con.cursor()
        cursorObj.execute(query, values)
        con.commit()
        desconectar()
    except Error as e:
        print(e)


def eliminar_guardadas(id_usuario, id_imagen):
    '''
    Registra en la base de datos que a un usuario ya no le gusta una imagen
    de otro usuario.
    '''
    query = "DELETE FROM MeGusta WHERE id_usuario=? AND id_imagen=?;"
    values = (id_usuario, id_imagen)
    try:
        con = conectar()
        cursorObj = con.cursor()
        cursorObj.execute(query, values)
        con.commit()
        desconectar()
    except Error:
        print(Error)


def insertar_imagen_etiqueta(id_imagen, id_etiqueta):
    '''
    Asocia una imagen a una etiqueta en la base de datos
    '''
    query = """INSERT INTO Imagenes_Etiquetas (id_imagen, id_etiqueta) 
               VALUES (?, ?);"""
    values = (id_imagen, id_etiqueta)
    try:
        con = conectar()
        cursorObj = con.cursor()
        cursorObj.execute(query, values)
        con.commit()
        desconectar()
    except Error as e:
        print(e)


def eliminar_imagen_etiqueta(id_imagen, id_etiqueta):
    '''
    Elimina la asociación entre una imagen y una etiqueta
    '''
    query = "DELETE Imagenes_Etiquetas WHERE id_imagen=? AND id_etiqueta=?);"
    values = (id_imagen, id_etiqueta)
    try:
        con = conectar()
        cursorObj = con.cursor()
        cursorObj.execute(query, values)
        con.commit()
        desconectar()
        
    except Error as e:
        print(e)


def validar_ruta(ruta):
    '''
    Retorna False si la ruta se encuentra en el servidor y True si no está.
    '''
    query = "SELECT id from Imagenes WHERE ruta=?;"
    values = (f"'{ruta}'",)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        res = cursor.fetchone()
        desconectar()
        return True if res is None else False
    except Error as e:
        print(e)


def insertar_imagen(nombre_imagen, id_usuario, ruta, privada, etiquetas):
    '''
    Inserta una imagen en la base de datos
    '''
    query = """INSERT INTO Imagenes (nombre_imagen, id_usuario, ruta, privada)
               VALUES(?, ?, ?, ?);"""
    values = (f"'{nombre_imagen}'", id_usuario, f"'{ruta}'", 1 if privada else 0)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)            
        con.commit()
        desconectar()
        
        imgId = get_id_imagen(ruta)
        for etiqueta in etiquetas:
            insertar_etiqueta(etiqueta)
            insertar_imagen_etiqueta(imgId, get_id_etiqueta(etiqueta))

    except Error as e:
        print(e)


def get_id_imagen(ruta):
    '''
    Retorna el id de una imagen dada su ruta
    '''
    query = "SELECT id FROM Imagenes WHERE ruta=?;"
    values = (f"'{ruta}'",)
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.execute(query, values)
        res = cursor.fetchone()
        desconectar()
        return res if res is None else res[0]
        
    except Error as e:
        print(e)


def actualizar_imagen(id_, nombre_imagen, ruta, privada, etiquetas):
    '''
    Actualiza los datos de una imagen en la base de datos
    '''
    query = """UPDATE Imagenes 
               SET nombre_imagen=?, ruta=?, privada=?
               WHERE id=?;"""
    values = (f"'{nombre_imagen}'", f"'{ruta}'", 1 if privada else 0, id_)
    try:
        con = conectar()
        cursorObj = con.cursor()
        cursorObj.execute(query, values)
        # retirar asociaciones a la imagen de MeGusta si se vuelve privada
        if privada:
            cursorObj.execute("DELETE FROM MeGusta WHERE id_imagen=?;", (id_,)) 
        con.commit()
        desconectar()
        
        # obtener lista de etiquetas antes de la actualizacion
        etiquetas_old = get_etiquetas(id_)
        # recorrer la lista de etiquetas más corta entre la nueva y la anterior
        etiquetas_aux = etiquetas_old if len(etiquetas_old) < len(etiquetas) else etiquetas
        for e in etiquetas_aux:
            # si un elemento está en ambas listas, eliminarlo de ambas
            if (e in etiquetas_old) and (e in etiquetas):
                etiquetas_old.remove(e)
                etiquetas.remove(e)
        # los elementos que queden en etiquetas hay que agregarlos/asociarlos a la imagen
        for e in etiquetas:
            insertar_etiqueta(e)
            insertar_imagen_etiqueta(id_, get_id_etiqueta(e))
        # para los elementos que queden en etiquetas_old hay que eliminar su relación con la imagen
        for e in etiquetas_old:
            eliminar_imagen_etiqueta(id_, get_id_etiqueta(e))

    except Error as e:
        print(e)

def eliminar_imagen(id_):
    '''
    Elimina los datos de una imagen de la base de datos, incluyendo sus
    asociaciones a etiquetas y a usuarios que le dieron 'me gusta'
    '''
    # 1. Eliminar referencias a la imagen en la tabla MeGusta
    # 2. Eliminar referencias a la imagen en la tabla Imagenes_etiquetas
    # 3. Eliminar registro en tabla Imagenes
    queries =  [
        "DELETE FROM MeGusta WHERE id_imagen=?;",
        "DELETE FROM Imagenes_Etiquetas WHERE id_imagen=?;",
        "DELETE FROM Imagenes WHERE id=?;"
    ]
    values = (id_,)
    try:
        con = conectar()
        cursorObj = con.cursor()
        for query in queries: 
            cursorObj.execute(query, values)
        con.commit()
        desconectar()
    except Error as e:
        print(e)

def buscar_imagenes(palabras_clave):
    '''
    Recibe una lista de palabras clave para buscar por nombre y etiqueta en 
    la base de datos y retorna una lista de imagenes, donde cada imagen es un 
    diccionario con las llaves id, nombre, ruta y etiquetas; siendo ésta última
    una lista. Solo se retornan imagenes publicas
    '''
    query = """SELECT I.id, I.nombre_imagen, I.ruta FROM Imagenes AS I
               WHERE  I.nombre_imagen LIKE ? AND privada=0
               UNION
               SELECT I.id, I.nombre_imagen I.ruta FROM Imagenes AS I
               INNER JOIN Imagenes_Etiquetas AS IE ON IE.id_imagen = I.id
               INNER JOIN Etiquetas AS E ON E.id_etiqueta = IE.id_etiqueta
               WHERE E.nombre_etiqueta LIKE ? AND privada=0;"""
    values = [(f"'%{kw}%'", f"'%{kw}%'") for kw in palabras_clave]
    try:
        con = conectar()
        cursor = con.cursor()
        cursor.executemany(query, values)
        imagenes = cursor.fetchall()
        desconectar()
        desconectar()
        # convertir el resultado a una lista de diccionarios
        keys = ['id', 'nombre', 'ruta']
        imagenes = [{k:v for k,v in zip(keys,img)} for img in imagenes]
        for img in imagenes: 
            img['etiquetas'] = get_etiquetas(img['id'])

        return imagenes
    except Error as e:
        print(e)
        