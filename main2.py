from flask import Flask, request, jsonify, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from datetime import datetime, timedelta
from flask_cors import CORS
from sqlalchemy import desc, func
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maison.db'
db = SQLAlchemy(app)
CORS(app)
app.secret_key = "Amboara"
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

AUTHORIZED_USER = [4, 5]
AUTHORIZED_USER_2 = [1, 2]

current_month = datetime.now().month
current_year = datetime.now().year


# Modèle pour les tâches
class Tache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100))

# Modèle pour les chambres
class Chambre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)


#Chat
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    user_name = db.Column(db.String, nullable=False)

#Modèle de payement elec et User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    room_number = db.Column(db.Integer, nullable=False)
    matricule = db.Column(db.Integer, nullable=False, unique=True)
    es = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class MonthlyPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    water_paid = db.Column(db.Boolean, default=False)
    electricity_paid = db.Column(db.Boolean, default=False)


# Modèle pour les remarques
class Remarque(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambre.id'))
    tache_id = db.Column(db.Integer, db.ForeignKey('tache.id'))
    date = db.Column(db.DateTime, default=datetime.now)
    remarque = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'chambre_id': self.chambre_id,
            'tache_id': self.tache_id,
            'date': self.date,
            'remarque': self.remarque
        }
    @staticmethod
    def get_latest_remark(user_id):
        return Remarque.query.filter_by(user_id=user_id).order_by(desc(Remarque.date)).first()
    
class WaterPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.now)

# Modèle pour le paiement de l'électricité
class ElectricityPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.now)


    
students_data = [
    {"name": "Niavo", "room_number": 1, "matricule": 12345, "password": "T4r3!2$L@", "es":"ETS"},
    {"name": "Michel", "room_number": 1, "matricule": 23456, "password": "&M%n9*u(i", "es":"IST"},
    {"name": "Aristino", "room_number": 2, "matricule": 34567, "password": "?aZ7eR5tY", "es":"CFRH"},
    {"name": "Sitraka", "room_number": 2, "matricule": 45678, "password": "#E$c4v%bX", "es":"IST"},
    {"name": "Ronico", "room_number": 3, "matricule": 56789, "password": "+D*f3w%sA", "es":"ETS"},
    {"name": "Nantenaina", "room_number": 3, "matricule": 67890, "password": "-G^h2j%zM", "es":"ISPM"},
    {"name": "Amboara", "room_number": 4, "matricule": 78901, "password": "=H&j4k%lP", "es":"ISPM"},
    {"name": "Parson", "room_number": 4, "matricule": 89201, "password": "/I'k5l%mQ", "es":"CFRH"}
]
semaine_taches = {
    'A': {
        'Lundi': {'Tache 1': 'Chambre 4', 'Tache 2': 'Chambre 2', 'Tache 3': 'Chambre 1', 'Tache 4': 'Chambre 3'},
        'Mardi': {'Tache 1': 'Chambre 3', 'Tache 2': 'Chambre 1', 'Tache 3': 'Chambre 2', 'Tache 4': 'Chambre 4'},
        'Mercredi': {'Tache 1': 'Chambre 2', 'Tache 2': 'Chambre 4', 'Tache 3': 'Chambre 3', 'Tache 4': 'Chambre 1'},
        'Jeudi': {'Tache 1': 'Chambre 1', 'Tache 2': 'Chambre 3', 'Tache 3': 'Chambre 4', 'Tache 4': 'Chambre 2'},
        'Vendredi': {'Tache 1': 'Chambre 4', 'Tache 2': 'Chambre 2', 'Tache 3': 'Chambre 1', 'Tache 4': 'Chambre 3'},
        'Samedi': None,
        'Dimanche': None
    },
    'B': {
        'Lundi': {'Tache 1': 'Chambre 3', 'Tache 2': 'Chambre 4', 'Tache 3': 'Chambre 2', 'Tache 4': 'Chambre 1'},
        'Mardi': {'Tache 1': 'Chambre 4', 'Tache 2': 'Chambre 1', 'Tache 3': 'Chambre 3', 'Tache 4': 'Chambre 2'},
        'Mercredi': {'Tache 1': 'Chambre 1', 'Tache 2': 'Chambre 2', 'Tache 3': 'Chambre 4', 'Tache 4': 'Chambre 3'},
        'Jeudi': {'Tache 1': 'Chambre 2', 'Tache 2': 'Chambre 4', 'Tache 3': 'Chambre 1', 'Tache 4': 'Chambre 4'},
        'Vendredi': {'Tache 1': 'Chambre 3', 'Tache 2': 'Chambre 4', 'Tache 3': 'Chambre 2', 'Tache 4': 'Chambre 1'},
        'Samedi': None,
        'Dimanche': None
    },
    'C': {
        'Lundi': {'Tache 1': 'Chambre 2', 'Tache 2': 'Chambre 1', 'Tache 3': 'Chambre 3', 'Tache 4': 'Chambre 4'},
        'Mardi': {'Tache 1': 'Chambre 1', 'Tache 2': 'Chambre 3', 'Tache 3': 'Chambre 4', 'Tache 4': 'Chambre 2'},
        'Mercredi': {'Tache 1': 'Chambre 3', 'Tache 2': 'Chambre 4', 'Tache 3': 'Chambre 2', 'Tache 4': 'Chambre 1'},
        'Jeudi': {'Tache 1': 'Chambre 4', 'Tache 2': 'Chambre 2', 'Tache 3': 'Chambre 1', 'Tache 4': 'Chambre 3'},
        'Vendredi': {'Tache 1': 'Chambre 2', 'Tache 2': 'Chambre 1', 'Tache 3': 'Chambre 3', 'Tache 4': 'Chambre 4'},
        'Samedi': None,
        'Dimanche': None
    }
}
def create_users():
    with app.app_context():
        db.create_all()
        for student in students_data:
            user = User.query.filter_by(matricule=student['matricule']).first()
            if not user:
                new_user = User(name=student['name'], room_number=student['room_number'], matricule=student['matricule'], password=student['password'], es=student['es'])
                db.session.add(new_user)
        db.session.commit()

def verify_token(token):
    matricule, password = token.split(":")
    user = User.query.filter_by(matricule=matricule).first()
    if user and user.password == password:
        return True
    return False



def generer_taches():
    # Ajouter les tâches dans la base de données
    for semaine, jours in semaine_taches.items():
        for jour, taches in jours.items():
            # Vérifier si des tâches existent pour le jour actuel
            if taches:
                for tache_nom, chambre_nom in taches.items():
                    tache = Tache.query.filter_by(nom=tache_nom).first()
                    if not tache:
                        tache = Tache(nom=tache_nom)
                        db.session.add(tache)
                        db.session.commit()
                    chambre = Chambre.query.filter_by(numero=int(chambre_nom.split()[-1])).first()
                    if chambre:
                        nouvelle_remarque = Remarque(chambre_id=chambre.id, tache_id=tache.id)
                        db.session.add(nouvelle_remarque)
    db.session.commit()

from collections import defaultdict




@app.route('/profil', methods=['GET'])
def get_profil():

    def get_fr_day_of_week():
        jours_semaine = {
            0: 'Lundi',
            1: 'Mardi',
            2: 'Mercredi',
            3: 'Jeudi',
            4: 'Vendredi',
            5: 'Samedi',
            6: 'Dimanche'
        }
        return jours_semaine[datetime.now().weekday()]

    # Utilisation de la fonction pour récupérer le jour de la semaine en français
    jour_semaine = get_fr_day_of_week()

    token = request.headers.get('Authorization')
    if not token or not verify_token(token):
        return jsonify({"msg": "Accès non autorisé"}), 401

    matricule, _ = token.split(":")
    user = User.query.filter_by(matricule=matricule).first()
    if not user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404

    # Récupérer la semaine actuelle (A, B ou C)
    semaine_courante_index = (datetime.now().isocalendar()[1] - 1) % 3
    semaines = ['C', 'A', 'B']
    semaine_courante = semaines[semaine_courante_index]

    # Vérifier si des tâches existent pour le jour actuel et la semaine courante
    if semaine_courante not in semaine_taches or jour_semaine not in semaine_taches[semaine_courante]:
        return jsonify({"msg": "Aucune tâche pour aujourd'hui"}), 404

    # Récupérer les tâches pour le jour actuel et la semaine courante
    taches_semaine = semaine_taches[semaine_courante][jour_semaine]

    # Filtrer les tâches pour la chambre de l'utilisateur
    chambre_utilisateur = f'Chambre {user.room_number}'
    tache_utilisateur = {key: value for key, value in taches_semaine.items() if value == chambre_utilisateur}

    latest_remark = Remarque.get_latest_remark(user.id)
    latest_remark_data = latest_remark.to_dict() if latest_remark else None

    return jsonify({
        "name": user.name,
        "room_number": user.room_number,
        "es": user.es,
        "current_task": tache_utilisateur,
        "latest_remark": latest_remark_data
    }), 200




@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Requête JSON attendue"}), 400

    matricule = request.json.get('matricule', None)
    password = request.json.get('password', None)

    if not matricule or not password:
        return jsonify({"msg": "Matricule ou mot de passe manquant"}), 400

    user = User.query.filter_by(matricule=matricule).first()

    if not user or user.password != password:
        return jsonify({"msg": "Identifiant ou mot de passe incorrect"}), 401

    token = f"{matricule}:{password}"
    return jsonify({"token": token}), 200


@app.route('/logout', methods=['POST'])
def logout():
    if 'Authorization' in request.headers:
        del request.headers['Authorization']
        return jsonify({"msg": "Déconnexion réussie"}), 200
    else:
        return jsonify({"msg": "Aucun token trouvé"}), 400

@app.route('/taches/<string:semaine>/<string:jour>', methods=['GET'])
def get_taches_jour(semaine, jour):
    if semaine not in semaine_taches or jour not in semaine_taches[semaine] and jour != 'All':
        return "Semaine ou jour non valide", 400

    # Récupérer les tâches pour le jour spécifié
    if jour == 'All':
        taches = semaine_taches[semaine]
    else: 
        taches = semaine_taches[semaine][jour]

    # Vérifier si des tâches existent pour ce jour
    if taches:
        return jsonify(taches)
    else:
        return f"Aucune tâche pour le jour {jour} de la semaine {semaine}", 404




@app.route('/ajouter_remarque', methods=['POST'])
def ajouter_remarque():
    token = request.headers.get('Authorization')
    if not token or not verify_token(token):
        return jsonify({"msg": "Accès non autorisé"}), 401

    user_matricule, _ = token.split(":")
    current_user = User.query.filter_by(matricule=user_matricule).first()
    if not current_user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404

    if current_user.id not in AUTHORIZED_USER:
        return jsonify({"msg": "Accès non autorisé pour cet utilisateur"}), 403

    data = request.json
    if not data or 'matricule' not in data or 'remarque' not in data:
        return jsonify({'error': 'Les données JSON sont incomplètes'}), 400

    user = User.query.filter_by(matricule=data['matricule']).first()
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    Remarque.query.filter_by(user_id=user.id).delete()

    nouvelle_remarque = Remarque(user_id=user.id, remarque=data['remarque'])
    db.session.add(nouvelle_remarque)
    db.session.commit()
    return jsonify({'message': 'Remarque ajoutée avec succès'}), 201


@app.route('/dernieres_remarques', methods=['GET'])
def dernieres_remarques():
    token = request.headers.get('Authorization')
    if not token or not verify_token(token):
        return jsonify({"msg": "Accès non autorisé"}), 401

    user_matricule, _ = token.split(":")
    current_user = User.query.filter_by(matricule=user_matricule).first()
    if not current_user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404

    if current_user.id not in AUTHORIZED_USER:
        return jsonify({"msg": "Accès non autorisé pour cet utilisateur"}), 403

    last_remarks = {}
    users = User.query.all()
    for user in users:
        last_remark = Remarque.query.filter_by(user_id=user.id).order_by(desc(Remarque.date)).first()
        if last_remark:
            last_remarks[user.name] = last_remark.remarque

    return jsonify(last_remarks), 200


def effacer_remarques_hebdomadaires():
    today = datetime.today()
    if today.weekday() == 0:
        Remarque.query.delete()
        db.session.commit()


effacer_remarques_hebdomadaires()

from sqlalchemy import and_

@app.route('/user/<int:user_id>/water_payment', methods=['POST'])
def update_water_payment(user_id):
    token = request.headers.get('Authorization')
    if not token or not verify_token(token):
        return jsonify({"msg": "Accès non autorisé"}), 401

    user_matricule, _ = token.split(":")
    current_user = User.query.filter_by(matricule=user_matricule).first()
    if not current_user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404

    if current_user.id not in AUTHORIZED_USER_2:
        return jsonify({"msg": "Accès non autorisé pour cet utilisateur"}), 403

    data = request.json
    if not data or 'user_matricule' not in data:
        return jsonify({'error': 'Matricule de l\'utilisateur requis'}), 400
    
    user = User.query.filter_by(matricule=data['user_matricule']).first()
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Supprimer les anciennes entrées de paiement d'eau pour cet utilisateur
    WaterPayment.query.filter_by(user_id=user.id).delete()

    water_payment = WaterPayment(user_id=user.id)
    db.session.add(water_payment)
    db.session.commit()
    
    return jsonify({"message": f"Paiement de l'eau enregistré avec succès pour l'utilisateur avec le matricule {data['user_matricule']}"}), 201


@app.route('/user/<int:user_id>/electricity_payment', methods=['POST'])
def update_electricity_payment(user_id):
    token = request.headers.get('Authorization')
    if not token or not verify_token(token):
        return jsonify({"msg": "Accès non autorisé"}), 401

    user_matricule, _ = token.split(":")
    current_user = User.query.filter_by(matricule=user_matricule).first()
    if not current_user:
        return jsonify({"msg": "Utilisateur non trouvé"}), 404

    if current_user.id not in AUTHORIZED_USER_2:
        return jsonify({"msg": "Accès non autorisé pour cet utilisateur"}), 403

    data = request.json
    if not data or 'user_matricule' not in data:
        return jsonify({'error': 'Matricule de l\'utilisateur requis'}), 400
    
    user = User.query.filter_by(matricule=data['user_matricule']).first()
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Supprimer les anciennes entrées de paiement d'électricité pour cet utilisateur
    ElectricityPayment.query.filter_by(user_id=user.id).delete()

    electricity_payment = ElectricityPayment(user_id=user.id)
    db.session.add(electricity_payment)
    db.session.commit()
    
    return jsonify({"message": f"Paiement de l'électricité enregistré avec succès pour l'utilisateur avec le matricule {data['user_matricule']}"}), 201




@app.route('/paiements/eau', methods=['GET'])
def get_water_payments():
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    water_payments = WaterPayment.query.filter(
        func.extract('month', WaterPayment.payment_date) == current_month,
        func.extract('year', WaterPayment.payment_date) == current_year
    ).all()
    water_payments_info = []
    for water_payment in water_payments:
        user = User.query.get(water_payment.user_id)
        water_payment_info = {
            "user_name": user.name,
            "payment_date": water_payment.payment_date.strftime("%Y-%m-%d")
        }
        water_payments_info.append(water_payment_info)

    return jsonify(water_payments_info), 200



@app.route('/paiements/electricite', methods=['GET'])
def get_electricity_payments():

    current_month = datetime.now().month
    current_year = datetime.now().year
    electricity_payments = ElectricityPayment.query.filter(
        func.extract('month', ElectricityPayment.payment_date) == current_month,
        func.extract('year', ElectricityPayment.payment_date) == current_year
    ).all()

    electricity_payments_info = []
    for electricity_payment in electricity_payments:
        user = User.query.get(electricity_payment.user_id)
        electricity_payment_info = {
            "user_name": user.name,
            "payment_date": electricity_payment.payment_date.strftime("%Y-%m-%d")
        }
        electricity_payments_info.append(electricity_payment_info)

    return jsonify(electricity_payments_info), 200





@app.route('/chat', methods=['POST'])
def add_chat_message():
    token = request.headers.get('Authorization')
    if not token or not verify_token(token):
        return jsonify({"msg": "Accès non autorisé"}), 401

    user_matricule = token.split(':')[0]

    data = request.get_json()
    content = data.get('content')
    if content:

        if not user_matricule.isdigit():
            return jsonify({'error': 'Matricule utilisateur non valide'}), 400

        user = User.query.filter_by(matricule=user_matricule).first()
        if not user:
            return jsonify({"msg": "Utilisateur non trouvé"}), 404

        message = Message(content=content, user_id=user.id, user_name=user.name, user_matricule=user_matricule)
        db.session.add(message)
        db.session.commit()
        return jsonify({'message': 'Message ajouté avec succès', 'user_name': user.name}), 201
    else:
        return jsonify({'error': 'Le contenu du message est requis'}), 400

@app.route('/chat', methods=['GET'])
def get_chat_messages():
    token = request.headers.get('Authorization')
    if not token or not verify_token(token):
        return jsonify({"msg": "Accès non autorisé"}), 401

    user_matricule = token.split(':')[0]

    recent_messages = Message.query.order_by(desc(Message.id)).limit(5).all()

    result = []
    for message in recent_messages:
        message_data = {
            'content': message.content,
            'user_name': message.user_name,
            'matricule': message.user_matricule
        }
        result.append(message_data)
    return jsonify(result)

@app.route('/paiements', methods=['GET'])
def get_paiements():
    token = request.headers.get('Authorization')
    if not token or not verify_token(token):
        return jsonify({"msg": "Accès non autorisé"}), 401
    
    # Vérifier si l'utilisateur a le droit d'accéder à cette route
    user_matricule, _ = token.split(":")
    user = User.query.filter_by(matricule=user_matricule).first()

    paiements = MonthlyPayment.query.all()
    paiements_info = []
    for paiement in paiements:
        user = User.query.get(paiement.user_id)
        paiement_info = {
            "user_id": paiement.user_id,
            "user_name": user.name,
            "room_number": user.room_number,
            "month": paiement.month,
            "year": paiement.year,
            "water_paid": paiement.water_paid,
            "electricity_paid": paiement.electricity_paid
        }
        paiements_info.append(paiement_info)

    return jsonify(paiements_info), 200

if __name__ == '__main__':
    create_users()
    app.run(debug=True)