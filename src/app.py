"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)

# [GET] /people Listar todos los registros de people en la base de datos.


@app.route('/people', methods=['GET'])
def get_people():
    # consultar todos los registros de la tabla
    people_query = People.query.all()
    # Convertimos los objetos de python a una lista de diccionarios JSON (bucle for)
    results = [person.serialize() for person in people_query]
    # Retornamos la lista con codigo 200 (ok)
    return jsonify(results), 200

# [GET] /people/<int:people_id> Muestra la información de un solo personaje según su id.


@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person = People.query.get(people_id)

    if person is None:
        return jsonify({"msg": "Ese personaje no existe en esta galaxia"}), 404

    return jsonify(person.serialize()), 200

# [GET] /planets Listar todos los registros de planets en la base de datos.


@app.route('/planets', methods=['GET'])
def get_planet():
    # consultar todos los registros de la tabla
    planets_query = Planet.query.all()
    # Convertimos los objetos de python a una lista de diccionarios JSON (bucle for)
    results = [planet.serialize() for planet in planets_query]
    # Retornamos la lista con codigo 200 (ok)
    return jsonify(results), 200

# [GET] /planets/<int:planet_id> Muestra la información de un solo planeta según su id.


@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)

    if planet is None:
        return jsonify({"msg": "Ese planeta no existe en esta galaxia"}), 404

    return jsonify(planet.serialize()), 200

# [GET] /users Listar todos los usuarios del blog.


@app.route('/users', methods=['GET'])
def get_users():
    users_query = User.query.all()
    results = [user.serialize() for user in users_query]
    return jsonify(results), 200

# [GET] /users/favorites Listar todos los favoritos que pertenecen al usuario actual.


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    # Simulamos que somos el usuario con ID 1 ya que aun no hay login
    current_user_id = 1
    # Buscamos en la tabla Favorite todos los que tengan user_id == 1
    # Usamos .filter_by() para filtrar
    favorites_query = Favorite.query.filter_by(user_id=current_user_id).all()
    # Serializamos la lista de favoritos
    results = [fav.serialize() for fav in favorites_query]

    return jsonify(results), 200

# [POST] /favorite/planet/<int:planet_id> Añade un nuevo planet favorito al usuario actual con el id = planet_id.


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    # Simular usuario ID 1
    user_id = 1
    # 1. VALIDACION si ya existe el favorito en la base de datos.
    # Se busca un registro que coincida con los dos IDs
    exist = Favorite.query.filter_by(user_id=1, planet_id=planet_id).first()

    if exist:
        # Si "exist" no es None, quiere decir que el planeta ya esta en favoritos
        return jsonify({"msg": "El usuario ya tiene este planeta en sus favoritos"}), 400
    # 2. Si el planeta no existe se agrega a Favoritos
    # 3. Se crea una nueva instancia del modelo Favorite
    # Le pasamos el usuario y el planeta que queremos conectar
    new_favorite = Favorite(user_id=user_id, planet_id=planet_id)
    # 4. La session de la DB es como un carrito de compra
    try:
        db.session.add(new_favorite)  # Metemos el cambio al carrito
        db.session.commit()          # Pagamos/confirmamos la transaccio
        return jsonify({"msg": "Planeta agregado a favoritos"}), 201
    except Exception as error:
        # Si algo falla durante el commit, "limpiamos" el carrito de la base de datos para que no se quede trabado con errores.
        db.session.rollback()
        return jsonify({"msg": "Error al guardar: " + str(error)}), 500


# [POST] /favorite/people/<int:people_id> Añade un nuevo people favorito al usuario actual con el id = people_id.

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    # Simular usuario ID 1
    user_id = 1
    # 1. VALIDACION si ya existe el favorito en la base de datos.
    # Se busca un registro que coincida con los dos IDs
    exist = Favorite.query.filter_by(user_id=1, people_id=people_id).first()

    if exist:
        # Si "exist" no es None, quiere decir que el planeta ya esta en favoritos
        return jsonify({"msg": "El usuario ya tiene este personaje en sus favoritos"}), 400
    # 2. Si el planeta no existe se agrega a Favoritos
    # 3. Se crea una nueva instancia del modelo Favorite
    # Le pasamos el usuario y el planeta que queremos conectar
    new_favorite = Favorite(user_id=user_id, people_id=people_id)
    # 4. La session de la DB es como un carrito de compra
    try:
        db.session.add(new_favorite)  # Metemos el cambio al carrito
        db.session.commit()          # Pagamos/confirmamos la transaccio
        return jsonify({"msg": "Personaje agregado a favoritos"}), 201
    except Exception as error:
        # Si algo falla durante el commit, "limpiamos" el carrito de la base de datos para que no se quede trabado con errores.
        db.session.rollback()
        return jsonify({"msg": "Error al guardar: " + str(error)}), 500


# [DELETE] /favorite/planet/<int:planet_id> Elimina un planet favorito con el id = planet_id.

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    # Simular usuario ID 1
    user_id = 1
    # 1 Buscamos el favorito en la DB
    favorite = Favorite.query.filter_by(
        user_id=user_id, planet_id=planet_id).first()

    if favorite is None:
        return jsonify({"msg": "Planeta favorito no encontrado"}), 404

    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": "Planeta eliminado de favoritos"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"msg": "Error al eliminar: " + str(error)}), 500


# [DELETE] /favorite/people/<int:people_id> Elimina un people favorito con el id = people_id.

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    # Simular usuario ID 1
    user_id = 1
    # 1 Buscamos el favorito en la DB
    favorite = Favorite.query.filter_by(
        user_id=user_id, people_id=people_id).first()

    if favorite is None:
        return jsonify({"msg": "Personaje favorito no encontrado"}), 404

    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": "Personaje eliminado de favoritos"}), 200
    except Exception as error:
        db.session.rollback()
        return jsonify({"msg": "Error al eliminar: " + str(error)}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
