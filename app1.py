from flask import Flask, request, jsonify, session, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///maison.db'
db = SQLAlchemy(app)
CORS(app)
app.secret_key = "Amboara"

AUTHORIZED_USER = [4, 5]
AUTHORIZED_USER_2 = [1, 2]

current_month = datetime.now().month
current_year = datetime.now().year

students_data = [
    {"name": "Niavo", "room_number": 1, "matricule": 12345, "password": "T4r3!2$L@"},
    {"name": "Michel", "room_number": 1, "matricule": 23456, "password": "&M%n9*u(i"},
    {"name": "Aristino", "room_number": 2, "matricule": 34567, "password": "?aZ7eR5tY"},
    {"name": "Sitraka", "room_number": 2, "matricule": 45678, "password": "#E$c4v%bX"},
    {"name": "Ronico", "room_number": 3, "matricule": 56789, "password": "+D*f3w%sA"},
    {"name": "Nantenaina", "room_number": 3, "matricule": 67890, "password": "-G^h2j%zM"},
    {"name": "Amboara", "room_number": 4, "matricule": 78901, "password": "=H&j4k%lP"},
    {"name": "Parson", "room_number": 4, "matricule": 89201, "password": "/I'k5l%mQ"}
]


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

#Modèle de payement elec et User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    room_number = db.Column(db.Integer, nullable=False)
    matricule = db.Column(db.Integer, nullable=False, unique=True)
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
    chambre_id = db.Column(db.Integer, db.ForeignKey('chambre.id'))
    tache_id = db.Column(db.Integer, db.ForeignKey('tache.id'))
    date = db.Column(db.DateTime, default=datetime.now)
    remarque = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'chambre_id': self.chambre_id,
            'tache_id': self.tache_id,
            'date': self.date,
            'remarque': self.remarque
        }

# Fonction pour générer les tâches pour les 3 semaines
def generer_taches():
    # Définir les tâches pour chaque jour de la semaine
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


@app.route('/taches/<string:semaine>/<string:jour>')
def get_taches(semaine, jour):
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    # Dictionnaire pour mapper les jours de la semaine aux tâches et aux chambres
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

    # Vérifier si la semaine et le jour sont valides
    if semaine not in semaine_taches or jour not in semaine_taches[semaine]:
        return "Semaine ou jour non valide", 400

    # Récupérer les tâches pour le jour et la semaine spécifiés
    taches = semaine_taches[semaine][jour]

    # Vérifier si des tâches existent pour ce jour
    if taches:
        return jsonify(taches)
    else:
        return f"Aucune tâche pour le jour {jour} de la semaine {semaine}", 404


@app.route('/tache_semaine/<string:semaine>')
def get_taches_semaines(semaine):
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    # Dictionnaire pour mapper les jours de la semaine aux tâches et aux chambres
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

    # Vérifier si la semaine et le jour sont valides
    if semaine not in semaine_taches:
        return "Semaine ou jour non valide", 400

    # Récupérer les tâches pour le jour et la semaine spécifiés
    taches = semaine_taches[semaine]

    # Vérifier si des tâches existent pour ce jour
    if taches:
        return jsonify(taches)
    else:
        return f"Tache de la semaines{semaine}", 404

@app.route('/remarques/<int:chambre_id>')
def get_remarques(chambre_id):
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    
    duree = request.args.get('duree', 'jour')
    if duree == 'jour':
        date_limite = datetime.now() - timedelta(days=1)
    elif duree == 'semaine':
        date_limite = datetime.now() - timedelta(weeks=1)
    elif duree == 'mois':
        date_limite = datetime.now() - timedelta(days=30)
    elif duree == 'annee':
        date_limite = datetime.now() - timedelta(days=365)
    remarques = Remarque.query.filter_by(chambre_id=chambre_id).filter(Remarque.date >= date_limite).all()
    return jsonify([remarque.to_dict() for remarque in remarques])



@app.route('/ajouter_remarque/<int:chambre_id>', methods=['POST'])
def ajouter_remarque(chambre_id):
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    
    user_matricule = session['user']['matricule']
    if user_matricule not in AUTHORIZED_USER:
        return jsonify({'message': 'Accès refusé : vous n\'êtes pas autorisé à ajouter une remarque pour cette chambre'}), 403
    
    data = request.json
    if not data or 'tache_id' not in data or 'remarque' not in data:
        return jsonify({'error': 'Les données JSON sont incomplètes'}), 400
    
    nouvelle_remarque = Remarque(chambre_id=chambre_id, tache_id=data['tache_id'], remarque=data['remarque'])
    db.session.add(nouvelle_remarque)
    db.session.commit()
    return jsonify({'message': 'Remarque ajoutée avec succès'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    matricule = data.get('matricule')
    password = data.get('password')

    # Recherche de l'utilisateur dans la base de données
    user = User.query.filter_by(matricule=matricule).first()

    if user and user.password == password:
        # Définir l'identifiant de session
        session['user'] = {
            'id': user.id,
            'name': user.name,
            'matricule': user.matricule
        }

        # Créer un cookie sécurisé
        response = make_response(jsonify({'message': 'Connexion réussie !'}))
        response.set_cookie('session_id', 'your_session_id', httponly=True, samesite='Strict')
        return response

    return jsonify({'message': 'Identifiants incorrects'}), 401

@app.route('/logout')
def logout():
    session.pop('user', None)
    response = make_response(jsonify({'message': 'Déconnexion réussie !'}))
    response.set_cookie('session_id', '', expires=0, httponly=True, samesite='Strict')
    return response

@app.route('/protected')
def protected():
    if 'user' in session:
        return jsonify({'message': 'Accès autorisé', 'user': session['user']})
    else:
        return jsonify({'message': 'Accès refusé'}), 401

@app.route('/user/<int:matricule>', methods=['GET'])
def get_user(matricule):
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    # Logique pour obtenir les détails de l'utilisateur par son matricule
    return jsonify({'message': 'Endpoint non implémenté'}), 501

@app.route('/users', methods=['GET'])
def get_users():
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    # Logique pour obtenir tous les utilisateurs
    return jsonify({'message': 'Endpoint non implémenté'}), 501



@app.route('/user/<int:user_id>/water_payment', methods=['POST'])
def update_water_payment(user_id):
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    
    current_user_id = session['user']['id']
    if current_user_id not in AUTHORIZED_USER_2:
        return jsonify({'message': 'Accès refusé : vous n\'êtes pas autorisé à effectuer cette action'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "Utilisateur non trouvé"}), 404

    now = datetime.now()
    month = now.month
    year = now.year

    payment = MonthlyPayment.query.filter_by(user_id=user_id, month=month, year=year).first()
    if not payment:
        payment = MonthlyPayment(user_id=user_id, month=month, year=year)

    payment.water_paid = True
    db.session.add(payment)
    db.session.commit()
    return jsonify({"message": "Paiement d'eau mis à jour avec succès"})

@app.route('/user/<int:user_id>/electricity_payment', methods=['POST'])
def update_electricity_payment(user_id):
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    
    current_user_id = session['user']['id']
    if current_user_id not in AUTHORIZED_USER_2:
        return jsonify({'message': 'Accès refusé : vous n\'êtes pas autorisé à effectuer cette action'}), 403
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"message": "Utilisateur non trouvé"}), 404

    now = datetime.now()
    month = now.month
    year = now.year

    payment = MonthlyPayment.query.filter_by(user_id=user_id, month=month, year=year).first()
    if not payment:
        payment = MonthlyPayment(user_id=user_id, month=month, year=year)

    payment.electricity_paid = True
    db.session.add(payment)
    db.session.commit()
    return jsonify({"message": "Paiement d'électricité mis à jour avec succès"})




@app.route('/payments', methods=['GET'])
def get_payments():
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    month = request.args.get('month')
    year = request.args.get('year')

    if month and year:
        payments = MonthlyPayment.query.filter_by(month=month, year=year).all()
    else:
        payments = MonthlyPayment.query.all()

    result = []
    for payment in payments:
        user = User.query.get(payment.user_id)
        payment_data = {
            "user_name": user.name,
            "room_number": user.room_number,
            "matricule": user.matricule,
            "month": payment.month,
            "year": payment.year,
            "water_paid": payment.water_paid,
            "electricity_paid": payment.electricity_paid
        }
        result.append(payment_data)
    return jsonify(result)

@app.route('/chat', methods=['GET'])
def get_chat_messages():
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    messages = Message.query.all()
    result = []
    for message in messages:
        user = User.query.get(message.user_id)
        message_data = {
            'id': message.id,
            'content': message.content,
            'user_name': user.name
        }
        result.append(message_data)
    return jsonify(result)

@app.route('/chat', methods=['POST'])
def add_chat_message():
    if 'user' not in session:
        return jsonify({'message': 'Vous devez être connecté pour effectuer cette action'}), 401
    data = request.get_json()
    content = data.get('content')
    if content:
        user_id = session['user']['id']
        message = Message(content=content, user_id=user_id)
        db.session.add(message)
        db.session.commit()
        return jsonify({'message': 'Message ajouté avec succès'}), 201
    else:
        return jsonify({'error': 'Le contenu du message est requis'}), 400


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        generer_taches()

    app.run(debug=True)