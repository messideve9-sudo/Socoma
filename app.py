import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from io import BytesIO
import json
import traceback

app = Flask(__name__)
# MODIFICATION POUR RENDER : utiliser os.environ
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'socoma-creances-2024-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///creances.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'warning'

# Données des 4 commerciaux COMPLETS
COMMERCIAUX_DATA = {
    'YAYA CAMARA': {
        'clients': [
            {'prenom': 'FANTA', 'nom': 'DIARRA', 'marche': 'BAGADADJI', 'contact': '76 42 79 10'},
            {'prenom': 'BROULAYE', 'nom': 'DIARRA', 'marche': 'BANCON FARADA', 'contact': '92 69 61 41'},
            {'prenom': 'SOULEYMANE', 'nom': 'TRAORE', 'marche': 'BANCONI FLABOUGOU', 'contact': '76 21 48 06'},
            {'prenom': 'MAHAMADOU', 'nom': 'DIAMOUTENE', 'marche': 'BOULKASSOUMBOUGOU', 'contact': '79 26 07 75'},
            {'prenom': 'MOUSSA', 'nom': 'CISSE', 'marche': 'DJALAKORODJI', 'contact': '72 61 29 81'},
            {'prenom': 'YAYA', 'nom': 'SOUKOULE', 'marche': 'DJELIBOUGOU', 'contact': '76 21 74 82'},
            {'prenom': 'AMINATA', 'nom': 'BALLO', 'marche': 'FADJIGUILA', 'contact': '77 71 70 06'},
            {'prenom': 'ABDOULAYE', 'nom': 'TRAORE', 'marche': 'KONATEBOUGOU', 'contact': '74 48 79 03'},
            {'prenom': 'FAH', 'nom': 'COULIBALY', 'marche': 'MARSEILLE', 'contact': '83 37 37 28'},
            {'prenom': 'DJIBRIL', 'nom': 'SIDIBE', 'marche': 'MEDINE', 'contact': '76 15 93 15'},
            {'prenom': 'SALIF', 'nom': 'DJOURTE', 'marche': 'MEDINE', 'contact': '76 19 26 65'},
            {'prenom': 'BA OUMAR', 'nom': 'SOUMOUNOU', 'marche': 'MEDINE', 'contact': '76 08 97 21'},
            {'prenom': 'ISSA', 'nom': 'DOLO', 'marche': 'MORIBABOUGOU', 'contact': '66 69 66 81'},
            {'prenom': 'ISSA', 'nom': 'DIAWARA', 'marche': 'NAFADJI', 'contact': '76 24 05 56'},
            {'prenom': 'ISSA', 'nom': 'FAMATA', 'marche': 'NGOLONINA', 'contact': '76 41 99 39'},
            {'prenom': 'ISSA', 'nom': 'TRAORE', 'marche': 'TITIBOUGOU', 'contact': '65 38 80 87'}
        ]
    },
    'BADRA KEITA': {
        'clients': [
            {'prenom': 'ALOU', 'nom': 'SIDIBE', 'marche': 'DIBIDANI', 'contact': '76 17 43 43'},
            {'prenom': 'DJELIKA', 'nom': 'KEITA', 'marche': 'DJICORONI PARA 1', 'contact': '66 87 40 20'},
            {'prenom': 'OUMOU', 'nom': 'SIDIBE', 'marche': 'DJICORONI PARA 2', 'contact': '76 06 11 40'},
            {'prenom': 'ABDOUL', 'nom': 'TOURE', 'marche': 'HAMDALAYE', 'contact': '75 33 89 43'},
            {'prenom': 'ISSA', 'nom': 'DIALLO', 'marche': 'HAMDALAYE', 'contact': '76 77 03 04'},
            {'prenom': 'MOUSSA', 'nom': 'TRAORE', 'marche': 'KANADJIGUILA', 'contact': '67 82 64 84'},
            {'prenom': 'IDRISSA', 'nom': 'KEITA', 'marche': 'KANADJIGUILA', 'contact': '66 83 10 40'},
            {'prenom': 'DJENABA', 'nom': 'DIARRA', 'marche': 'KATI CENTRAL', 'contact': '78 65 89 12'},
            {'prenom': 'SOUMAILA', 'nom': 'THIERO', 'marche': 'LAFIA BOUGOU 2 TRM', 'contact': '77 29 38 08'},
            {'prenom': 'BEDY', 'nom': 'KEITA', 'marche': 'LAFIA BOUGOU TALIKO', 'contact': '75 28 24 92'},
            {'prenom': 'MAH', 'nom': 'KONATE', 'marche': 'LAFIABOUGOU 1', 'contact': '74 05 15 45'},
            {'prenom': 'AROUNA DJIBRIL', 'nom': 'SIDIBE', 'marche': 'LAFIABOUGOU 2', 'contact': '74 67 72 13'},
            {'prenom': 'GOURO', 'nom': 'MAIGA', 'marche': 'NTOMIKOROBOUGOU', 'contact': '95 95 35 35'},
            {'prenom': 'AMIDOU', 'nom': 'KANTE', 'marche': 'SEBENICORO', 'contact': '76 15 36 71'},
            {'prenom': 'FATOUMATA', 'nom': 'BAGAYOKO', 'marche': 'WOLOFOBOUGOU', 'contact': '76 30 04 47'}
        ]
    },
    'ISSA DIAKITE': {
        'clients': [
            {'prenom': 'KADER', 'nom': 'TRAORE', 'marche': 'BACODJICORO ACI', 'contact': '65 14 66 80'},
            {'prenom': 'CHAKA', 'nom': 'DOUMBIA', 'marche': 'BACODJICORONI', 'contact': '74 10 62 67'},
            {'prenom': 'VIEUX', 'nom': 'DIABATE', 'marche': 'BADALABOUGOU', 'contact': '66 82 48 30'},
            {'prenom': 'AMIDOU', 'nom': 'KODIO', 'marche': 'DAOUDABOUGOU', 'contact': '76 38 66 41'},
            {'prenom': 'THIEMOKO', 'nom': 'SIDIBE', 'marche': 'GARANTIBOUGOU', 'contact': '76 62 23 39'},
            {'prenom': 'LASSINE', 'nom': 'TRAORE', 'marche': 'GOUANA', 'contact': '65 52 85 08'},
            {'prenom': 'MARIAM', 'nom': 'SANOGO', 'marche': 'KABALA', 'contact': '82 92 32 94'},
            {'prenom': 'MOUSSA', 'nom': 'KONE', 'marche': 'KALABAN ACI', 'contact': '70 88 61 49'},
            {'prenom': 'ABOU', 'nom': 'SAMAKE', 'marche': 'KALABAN ECHANGEUR', 'contact': '76 31 72 32'},
            {'prenom': 'ADAMA', 'nom': 'DIARRA', 'marche': 'KALABAN ECHANGEUR', 'contact': '70 93 37 25'},
            {'prenom': 'AMIDOU', 'nom': 'COULIBALY', 'marche': 'KALABAN KLOUBLENI', 'contact': '76 29 57 79'},
            {'prenom': 'AMINATA', 'nom': 'TRAORE', 'marche': 'KALABAN KORO', 'contact': '74 02 18 08'},
            {'prenom': 'SEYDOU', 'nom': 'DOUGNON', 'marche': 'KALABAN KOULOUBA', 'contact': '79 15 88 11'},
            {'prenom': 'MOUSSA', 'nom': 'GACKOU', 'marche': 'KALABAN PRINCIPAL', 'contact': '79 06 13 22'},
            {'prenom': 'NOUHOUM', 'nom': 'TRAORE', 'marche': 'NIAMAKORO KOURANI', 'contact': '66 41 55 31'},
            {'prenom': 'KAROUNGA', 'nom': 'DIARRA', 'marche': 'OLYMPE', 'contact': '78 11 92 59'},
            {'prenom': 'FATOUMATA', 'nom': 'DIAKITE', 'marche': 'SABALIBOUGOU', 'contact': '83 91 54 47'}
        ]
    },
    'DIDIER DEMBELE': {
        'clients': [
            {'prenom': 'SOULEYMANE', 'nom': 'GUINDO', 'marche': 'ALAMNA SOUGOU', 'contact': '70 51 95 77'},
            {'prenom': 'FATOUMATA', 'nom': 'CISSE', 'marche': 'ATT BOUGOU', 'contact': '60 16 20 83'},
            {'prenom': 'FAMOUGOURY', 'nom': 'SAMAKE', 'marche': 'BANANKABOUGOU', 'contact': '76 02 84 51'},
            {'prenom': 'BINTOU', 'nom': 'DIALLO', 'marche': 'MAGNAMBOUGOU', 'contact': '74 45 25 66'},
            {'prenom': 'ADAMA', 'nom': 'DIARRA', 'marche': 'MOUSSABOUGOU', 'contact': '78 20 10 20'},
            {'prenom': 'HAMA', 'nom': 'NANTOUME', 'marche': 'NIAMAKORO CHEZ BOUGOUNI', 'contact': '76 76 99 61'},
            {'prenom': 'MOUMINE', 'nom': 'DIAKITE', 'marche': 'NIAMAKORO SOUGOUKORO', 'contact': '76 44 19 38'},
            {'prenom': 'ISAC', 'nom': 'BERTHE', 'marche': 'NIAMAKORO SOUGOUKOURA', 'contact': '72 55 60 60'},
            {'prenom': 'TOGOLAIS', 'nom': 'YAO', 'marche': 'NIAMANA', 'contact': '70 89 66 17'},
            {'prenom': 'MOUSSA', 'nom': 'KEITA', 'marche': 'SABALIBOUGOU KOURANI', 'contact': '69 75 55 13'},
            {'prenom': 'DRAMANE', 'nom': 'OUATARRA', 'marche': 'SENOU', 'contact': '79 31 67 76'},
            {'prenom': 'ABDOULAYE', 'nom': 'DICKO', 'marche': 'SIRAKORO', 'contact': '76 44 42 87'},
            {'prenom': 'HAMADOUNE', 'nom': 'BAH', 'marche': 'SOGONIKO', 'contact': '72 01 12 73'},
            {'prenom': 'DJIBRYL', 'nom': 'SYLLA', 'marche': 'SOKORODJI', 'contact': '78 50 55 66'},
            {'prenom': 'BAMOULAYE', 'nom': 'TRAORE', 'marche': 'YIRIMADJO', 'contact': '76 19 45 67'},
            {'prenom': 'ISSA', 'nom': 'SAGARA', 'marche': 'ZERNI', 'contact': '76 25 18 81'}
        ]
    }
}

# Modèles de base de données
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    commercial = db.Column(db.String(100), nullable=True)
    date_creation = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Creance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    commercial = db.Column(db.String(100), nullable=False)
    client = db.Column(db.String(200), nullable=False)
    marche = db.Column(db.String(200), nullable=True)
    montant = db.Column(db.Float, nullable=False)
    versement = db.Column(db.Float, default=0)
    solde = db.Column(db.Float, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.now)
    date_facturation = db.Column(db.Date, nullable=False)
    date_echeance = db.Column(db.Date, nullable=True)
    jours_retard = db.Column(db.Integer, default=0)
    statut = db.Column(db.String(50), default='À RELANCER')
    situation_paiement = db.Column(db.String(50), default='EN COURS')
    commentaires = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.String(80), nullable=True)
    
    def update_statut(self):
        today = datetime.now().date()
        
        if self.solde <= 0:
            self.statut = 'PAYE'
            self.situation_paiement = 'SOLDE'
            self.jours_retard = 0
        elif self.date_echeance:
            if today > self.date_echeance:
                jours = (today - self.date_echeance).days
                self.jours_retard = jours
                if jours <= 3:
                    self.statut = 'À SURVEILLER'
                else:
                    self.statut = 'EN RETARD'
                self.situation_paiement = 'EN RETARD'
            elif today == self.date_echeance:
                self.statut = "AUJOURD'HUI"
                self.situation_paiement = 'À ÉCHÉANCE'
                self.jours_retard = 0
            elif (self.date_echeance - today).days <= 3:
                self.statut = 'À SURVEILLER'
                self.situation_paiement = 'À ÉCHÉANCE'
                self.jours_retard = 0
            else:
                self.statut = 'À RELANCER'
                self.situation_paiement = 'EN COURS'
                self.jours_retard = 0
        else:
            self.statut = 'À RELANCER'
            self.situation_paiement = 'EN COURS'
            self.jours_retard = 0

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Filtres Jinja2
@app.template_filter('format_money')
def format_money_filter(value):
    if value is None:
        return "0 FCFA"
    try:
        return f"{int(value):,} FCFA".replace(",", " ")
    except:
        return str(value)

@app.template_filter('format_date')
def format_date_filter(value):
    if not value:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, '%Y-%m-%d')
        except:
            return value
    return value.strftime('%d/%m/%Y')

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Routes principales
@app.route('/')
@login_required
def accueil():
    # Récupérer toutes les créances selon les permissions
    if current_user.role == 'commercial' and current_user.commercial:
        creances = Creance.query.filter_by(commercial=current_user.commercial).all()
    else:
        creances = Creance.query.all()
    
    # Calcul des statistiques
    total_creances = sum(c.montant for c in creances) if creances else 0
    total_versement = sum(c.versement for c in creances) if creances else 0
    total_solde = sum(c.solde for c in creances) if creances else 0
    
    creances_retard = [c for c in creances if c.situation_paiement == 'EN RETARD']
    montant_retard = sum(c.solde for c in creances_retard) if creances_retard else 0
    
    tpar = (montant_retard / total_creances * 100) if total_creances > 0 else 0
    
    # CORRECTION : Ajouter montant_a_solder
    montant_a_solder = total_solde
    
    # Statistiques par commercial
    stats_commerciaux = {}
    commerciaux_list = [current_user.commercial] if current_user.role == 'commercial' else COMMERCIAUX_DATA.keys()
    
    for commercial in commerciaux_list:
        if commercial:  # Vérifier que commercial n'est pas None
            comm_creances = [c for c in creances if c.commercial == commercial]
            total_comm = sum(c.montant for c in comm_creances)
            retard_comm = sum(c.solde for c in comm_creances if c.situation_paiement == 'EN RETARD')
            solde_comm = sum(c.solde for c in comm_creances)
            
            stats_commerciaux[commercial] = {
                'count': len(comm_creances),
                'total': total_comm,
                'retard': retard_comm,
                'solde': solde_comm,
                'clients': len(set(c.client for c in comm_creances))
            }
    
    return render_template('accueil.html',
                         total_creances=total_creances,
                         total_versement=total_versement,
                         total_solde=total_solde,
                         montant_retard=montant_retard,
                         montant_a_solder=montant_a_solder,  # CORRECTION AJOUTÉE
                         tpar=tpar,
                         creances_retard=creances_retard[:5],
                         stats_commerciaux=stats_commerciaux,
                         total_creances_en_cours=len([c for c in creances if c.solde > 0]))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('accueil'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            user.last_login = datetime.now()
            db.session.commit()
            login_user(user, remember=remember)
            flash(f'Bienvenue {username} !', 'success')
            return redirect(url_for('accueil'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnexion réussie', 'success')
    return redirect(url_for('login'))

@app.route('/creances')
@login_required
def liste_creances():
    # Construire la requête de base
    query = Creance.query
    
    # Appliquer les filtres selon le rôle
    if current_user.role == 'commercial' and current_user.commercial:
        query = query.filter_by(commercial=current_user.commercial)
    
    # Appliquer les filtres de l'URL
    commercial_filter = request.args.get('commercial')
    statut_filter = request.args.get('statut')
    client_filter = request.args.get('client')
    
    if commercial_filter:
        query = query.filter_by(commercial=commercial_filter)
    if statut_filter:
        query = query.filter_by(statut=statut_filter)
    if client_filter:
        query = query.filter(Creance.client.contains(client_filter))
    
    # Trier par date de création décroissante
    creances = query.order_by(Creance.date_creation.desc()).all()
    
    # Liste des commerciaux pour les filtres
    if current_user.role == 'commercial' and current_user.commercial:
        commerciaux_list = [current_user.commercial]
    else:
        commerciaux_list = list(COMMERCIAUX_DATA.keys())
    
    return render_template('liste_creances.html',
                         creances=creances,
                         commerciaux=commerciaux_list)

@app.route('/creances/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter_creance():
    # Vérifier les permissions
    if current_user.role == 'user':
        flash('Vous n\'avez pas la permission d\'ajouter des créances', 'error')
        return redirect(url_for('liste_creances'))
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            commercial = request.form.get('commercial')
            client_type = request.form.get('client_type')
            
            # Validation du commercial
            if current_user.role == 'commercial' and commercial != current_user.commercial:
                flash('Vous ne pouvez ajouter des créances que pour votre propre portefeuille', 'error')
                return redirect(url_for('ajouter_creance'))
            
            # Traitement du client
            if client_type == 'existant':
                client = request.form.get('client_select')
                marche = request.form.get('marche')
            else:
                prenom = request.form.get('nouveau_prenom', '').strip()
                nom = request.form.get('nouveau_nom', '').strip()
                if not prenom or not nom:
                    flash('Le prénom et le nom sont obligatoires', 'error')
                    return redirect(url_for('ajouter_creance'))
                client = f"{prenom} {nom}"
                marche = request.form.get('nouveau_marche', '').strip()
            
            # Validation des montants
            try:
                montant = float(request.form.get('montant', 0))
                versement = float(request.form.get('versement', 0))
            except ValueError:
                flash('Les montants doivent être des nombres valides', 'error')
                return redirect(url_for('ajouter_creance'))
            
            if montant <= 0:
                flash('Le montant doit être supérieur à 0', 'error')
                return redirect(url_for('ajouter_creance'))
            
            if versement < 0:
                flash('Le versement ne peut pas être négatif', 'error')
                return redirect(url_for('ajouter_creance'))
            
            if versement > montant:
                flash('Le versement ne peut pas dépasser le montant', 'error')
                return redirect(url_for('ajouter_creance'))
            
            solde = montant - versement
            
            # Traitement des dates
            date_facturation_str = request.form.get('date_facturation')
            if not date_facturation_str:
                flash('La date de facturation est obligatoire', 'error')
                return redirect(url_for('ajouter_creance'))
            
            try:
                date_facturation = datetime.strptime(date_facturation_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Format de date invalide', 'error')
                return redirect(url_for('ajouter_creance'))
            
            date_echeance_str = request.form.get('date_echeance')
            date_echeance = None
            if date_echeance_str:
                try:
                    date_echeance = datetime.strptime(date_echeance_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Format de date d\'échéance invalide', 'error')
                    return redirect(url_for('ajouter_creance'))
            
            commentaires = request.form.get('commentaires', '').strip()
            
            # Créer la nouvelle créance
            nouvelle_creance = Creance(
                commercial=commercial,
                client=client,
                marche=marche,
                montant=montant,
                versement=versement,
                solde=solde,
                date_facturation=date_facturation,
                date_echeance=date_echeance,
                commentaires=commentaires,
                created_by=current_user.username
            )
            
            # Mettre à jour le statut
            nouvelle_creance.update_statut()
            
            # Sauvegarder dans la base de données
            db.session.add(nouvelle_creance)
            db.session.commit()
            
            flash(f'Créance ajoutée avec succès pour {client} !', 'success')
            return redirect(url_for('liste_creances'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de l\'ajout: {str(e)}', 'error')
            print(f"Erreur détaillée: {traceback.format_exc()}")
    
    # Préparer les données pour le template
    commerciaux_disponibles = []
    if current_user.role == 'commercial':
        commerciaux_disponibles = [current_user.commercial]
    else:
        commerciaux_disponibles = list(COMMERCIAUX_DATA.keys())
    
    return render_template('ajouter_creance.html',
                         commerciaux=commerciaux_disponibles,
                         commerciaux_data=COMMERCIAUX_DATA)

@app.route('/creances/modifier/<int:id>', methods=['GET', 'POST'])
@login_required
def modifier_creance(id):
    creance = Creance.query.get_or_404(id)
    
    # Vérifier les permissions
    if current_user.role == 'commercial' and creance.commercial != current_user.commercial:
        flash('Vous n\'avez pas la permission de modifier cette créance', 'error')
        return redirect(url_for('liste_creances'))
    
    if request.method == 'POST':
        try:
            # Récupérer le nouveau versement
            versement_str = request.form.get('versement', '0')
            try:
                nouveau_versement = float(versement_str)
            except ValueError:
                flash('Le versement doit être un nombre valide', 'error')
                return redirect(url_for('modifier_creance', id=id))
            
            # Validation du versement
            if nouveau_versement < 0:
                flash('Le versement ne peut pas être négatif', 'error')
                return redirect(url_for('modifier_creance', id=id))
            
            if nouveau_versement > creance.montant:
                flash('Le versement ne peut pas dépasser le montant initial', 'error')
                return redirect(url_for('modifier_creance', id=id))
            
            # Mettre à jour la créance
            creance.versement = nouveau_versement
            creance.solde = creance.montant - nouveau_versement
            
            # Mettre à jour la date d'échéance si fournie
            date_echeance_str = request.form.get('date_echeance')
            if date_echeance_str:
                try:
                    creance.date_echeance = datetime.strptime(date_echeance_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Format de date d\'échéance invalide', 'error')
                    return redirect(url_for('modifier_creance', id=id))
            
            # Mettre à jour les commentaires
            creance.commentaires = request.form.get('commentaires', '').strip()
            
            # Mettre à jour le statut
            creance.update_statut()
            
            # Sauvegarder
            db.session.commit()
            
            flash('Créance modifiée avec succès !', 'success')
            return redirect(url_for('liste_creances'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'error')
    
    return render_template('modifier_creance.html', creance=creance)

@app.route('/creances/supprimer/<int:id>')
@login_required
def supprimer_creance(id):
    # Vérifier les permissions
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('liste_creances'))
    
    creance = Creance.query.get_or_404(id)
    
    try:
        client_name = creance.client
        db.session.delete(creance)
        db.session.commit()
        flash(f'Créance pour {client_name} supprimée avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('liste_creances'))

@app.route('/tableau-bord')
@login_required
def tableau_bord():
    # Récupérer les créances selon les permissions
    if current_user.role == 'commercial' and current_user.commercial:
        creances = Creance.query.filter_by(commercial=current_user.commercial).all()
    else:
        creances = Creance.query.all()
    
    # Statistiques globales
    total_creances = sum(c.montant for c in creances) if creances else 0
    total_versement = sum(c.versement for c in creances) if creances else 0
    total_solde = sum(c.solde for c in creances) if creances else 0
    
    creances_retard = [c for c in creances if c.situation_paiement == 'EN RETARD']
    montant_retard = sum(c.solde for c in creances_retard) if creances_retard else 0
    
    # CORRECTION : Ajouter montant_a_solder
    montant_a_solder = total_solde
    
    tpar = (montant_retard / total_creances * 100) if total_creances > 0 else 0
    
    # Statistiques par commercial
    stats_commerciaux = {}
    commerciaux_list = [current_user.commercial] if current_user.role == 'commercial' else COMMERCIAUX_DATA.keys()
    
    for commercial in commerciaux_list:
        if commercial:  # Vérifier que commercial n'est pas None
            comm_creances = [c for c in creances if c.commercial == commercial]
            total_comm = sum(c.montant for c in comm_creances)
            retard_comm = sum(c.solde for c in comm_creances if c.situation_paiement == 'EN RETARD')
            solde_comm = sum(c.solde for c in comm_creances)
            
            stats_commerciaux[commercial] = {
                'count': len(comm_creances),
                'total': total_comm,
                'retard': retard_comm,
                'solde': solde_comm
            }
    
    # Top retards
    top_retard = sorted(creances_retard, key=lambda x: x.jours_retard or 0, reverse=True)[:5]
    
    return render_template('tableau_bord.html',
                         total_creances=total_creances,
                         total_versement=total_versement,
                         total_solde=total_solde,
                         montant_retard=montant_retard,
                         montant_a_solder=montant_a_solder,  # CORRECTION AJOUTÉE
                         tpar=tpar,
                         creances_retard=creances_retard,
                         top_retard=top_retard,
                         stats_commerciaux=stats_commerciaux)

@app.route('/recap-clients')
@login_required
def recap_clients():
    # Récupérer les créances selon les permissions
    if current_user.role == 'commercial' and current_user.commercial:
        creances = Creance.query.filter_by(commercial=current_user.commercial).all()
    else:
        creances = Creance.query.all()
    
    # Groupement par client
    clients_data = {}
    for creance in creances:
        client_key = creance.client
        if client_key not in clients_data:
            clients_data[client_key] = {
                'client': creance.client,
                'commercial': creance.commercial,
                'marche': creance.marche,
                'nombre_creances': 0,
                'total_montant': 0,
                'total_versement': 0,
                'total_solde': 0,
                'derniere_echeance': None
            }
        
        clients_data[client_key]['nombre_creances'] += 1
        clients_data[client_key]['total_montant'] += creance.montant
        clients_data[client_key]['total_versement'] += creance.versement
        clients_data[client_key]['total_solde'] += creance.solde
        
        if creance.date_echeance and (not clients_data[client_key]['derniere_echeance'] or 
                                      creance.date_echeance > clients_data[client_key]['derniere_echeance']):
            clients_data[client_key]['derniere_echeance'] = creance.date_echeance
    
    clients_recap = list(clients_data.values())
    
    # Totaux
    total_montant = sum(c['total_montant'] for c in clients_recap)
    total_versement = sum(c['total_versement'] for c in clients_recap)
    total_solde = sum(c['total_solde'] for c in clients_recap)
    total_creances = len(creances)
    
    # Filtre par commercial
    selected_commercial = request.args.get('commercial')
    if selected_commercial and current_user.role != 'commercial':
        clients_recap = [c for c in clients_recap if c['commercial'] == selected_commercial]
    
    # Liste des commerciaux pour les filtres
    if current_user.role == 'commercial':
        commerciaux_list = [current_user.commercial]
    else:
        commerciaux_list = list(COMMERCIAUX_DATA.keys())
    
    return render_template('recap_clients.html',
                         clients_recap=clients_recap,
                         total_montant=total_montant,
                         total_versement=total_versement,
                         total_solde=total_solde,
                         total_creances=total_creances,
                         commerciaux=commerciaux_list,
                         selected_commercial=selected_commercial)

@app.route('/client/<string:client_name>')
@login_required
def detail_client(client_name):
    client_name = client_name.replace('_', ' ')
    
    # Construire la requête
    query = Creance.query.filter_by(client=client_name)
    
    # Vérifier les permissions
    if current_user.role == 'commercial' and current_user.commercial:
        query = query.filter_by(commercial=current_user.commercial)
    
    creances = query.order_by(Creance.date_creation.desc()).all()
    
    if not creances:
        flash('Client non trouvé ou vous n\'avez pas accès à ce client', 'error')
        return redirect(url_for('recap_clients'))
    
    # Calcul des totaux
    total_montant = sum(c.montant for c in creances) if creances else 0
    total_versement = sum(c.versement for c in creances) if creances else 0
    total_solde = sum(c.solde for c in creances) if creances else 0
    
    # Dernière date d'échéance
    dates_echeance = [c.date_echeance for c in creances if c.date_echeance]
    derniere_date = max(dates_echeance) if dates_echeance else None
    
    return render_template('detail_client.html',
                         client_name=client_name,
                         creances=creances,
                         total_montant=total_montant,
                         total_versement=total_versement,
                         total_solde=total_solde,
                         derniere_date=derniere_date)

@app.route('/commerciaux')
@login_required
def commerciaux():
    # Récupérer les créances selon les permissions
    if current_user.role == 'commercial' and current_user.commercial:
        creances = Creance.query.filter_by(commercial=current_user.commercial).all()
        commerciaux_list = [current_user.commercial]
    else:
        creances = Creance.query.all()
        commerciaux_list = list(COMMERCIAUX_DATA.keys())
    
    # Statistiques par commercial
    stats = {}
    for commercial in commerciaux_list:
        if commercial:  # Vérifier que commercial n'est pas None
            comm_creances = [c for c in creances if c.commercial == commercial]
            stats[commercial] = {
                'total_creances': len(comm_creances),
                'total_montant': sum(c.montant for c in comm_creances),
                'total_versement': sum(c.versement for c in comm_creances),
                'total_solde': sum(c.solde for c in comm_creances),
                'clients': len(set(c.client for c in comm_creances))
            }
    
    return render_template('commerciaux.html',
                         commerciaux=COMMERCIAUX_DATA,
                         stats=stats)

@app.route('/gestion-utilisateurs')
@login_required
def gestion_utilisateurs():
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('accueil'))
    
    utilisateurs = User.query.all()
    return render_template('gestion_utilisateurs.html', utilisateurs=utilisateurs)

@app.route('/creer-compte', methods=['GET', 'POST'])
@login_required
def creer_compte():
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('accueil'))
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            role = request.form.get('role', 'user')
            commercial = request.form.get('commercial', '').strip() if role == 'commercial' else None
            
            # Validation
            if not username:
                flash('Le nom d\'utilisateur est obligatoire', 'error')
                return redirect(url_for('creer_compte'))
            
            if not password:
                flash('Le mot de passe est obligatoire', 'error')
                return redirect(url_for('creer_compte'))
            
            if len(password) < 6:
                flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
                return redirect(url_for('creer_compte'))
            
            if role == 'commercial' and not commercial:
                flash('Vous devez sélectionner un commercial pour un compte commercial', 'error')
                return redirect(url_for('creer_compte'))
            
            # Vérifier si l'utilisateur existe déjà
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Ce nom d\'utilisateur existe déjà', 'error')
                return redirect(url_for('creer_compte'))
            
            # Créer le nouvel utilisateur
            nouvel_utilisateur = User(
                username=username,
                role=role,
                commercial=commercial
            )
            nouvel_utilisateur.set_password(password)
            
            # Sauvegarder
            db.session.add(nouvel_utilisateur)
            db.session.commit()
            
            flash(f'Compte créé avec succès pour {username} !', 'success')
            return redirect(url_for('gestion_utilisateurs'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la création du compte: {str(e)}', 'error')
    
    return render_template('creer_compte.html')

@app.route('/supprimer-utilisateur/<int:id>')
@login_required
def supprimer_utilisateur(id):
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('gestion_utilisateurs'))
    
    # Empêcher la suppression de son propre compte
    if current_user.id == id:
        flash('Vous ne pouvez pas supprimer votre propre compte', 'error')
        return redirect(url_for('gestion_utilisateurs'))
    
    utilisateur = User.query.get_or_404(id)
    
    try:
        username = utilisateur.username
        db.session.delete(utilisateur)
        db.session.commit()
        flash(f'Utilisateur {username} supprimé avec succès', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erreur lors de la suppression: {str(e)}', 'error')
    
    return redirect(url_for('gestion_utilisateurs'))

@app.route('/export-excel')
@login_required
def export_excel():
    # Récupérer les créances selon les permissions
    if current_user.role == 'commercial' and current_user.commercial:
        creances = Creance.query.filter_by(commercial=current_user.commercial).all()
    else:
        creances = Creance.query.all()
    
    # Préparer les données pour Excel
    data = []
    for creance in creances:
        data.append({
            'ID': creance.id,
            'Commercial': creance.commercial,
            'Client': creance.client,
            'Marché': creance.marche or '',
            'Montant (FCFA)': creance.montant,
            'Versement (FCFA)': creance.versement,
            'Solde (FCFA)': creance.solde,
            'Date Facturation': creance.date_facturation.strftime('%d/%m/%Y'),
            'Date Échéance': creance.date_echeance.strftime('%d/%m/%Y') if creance.date_echeance else '',
            'Jours Retard': creance.jours_retard or 0,
            'Statut': creance.statut,
            'Situation': creance.situation_paiement,
            'Commentaires': creance.commentaires or '',
            'Créé par': creance.created_by or '',
            'Date Création': creance.date_creation.strftime('%d/%m/%Y %H:%M')
        })
    
    # Créer le DataFrame
    df = pd.DataFrame(data)
    
    # Créer un fichier Excel en mémoire
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Créances', index=False)
        
        # Ajouter un résumé
        if current_user.role != 'commercial':
            summary_data = {
                'Commercial': list(COMMERCIAUX_DATA.keys()),
                'Nombre Clients': [len(COMMERCIAUX_DATA[c]['clients']) for c in COMMERCIAUX_DATA.keys()]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Résumé', index=False)
    
    output.seek(0)
    
    # Générer le nom du fichier
    filename = f'creances_socoma_{datetime.now().strftime("%Y%m%d_%H%M")}.xlsx'
    if current_user.role == 'commercial':
        filename = f'creances_{current_user.commercial.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d")}.xlsx'
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )

@app.route('/admin/reset-creances', methods=['GET', 'POST'])
@login_required
def admin_reset_creances():
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('accueil'))
    
    commercial_selected = request.args.get('commercial')
    stats = None
    
    if commercial_selected:
        query = Creance.query
        if commercial_selected != 'TOUS':
            query = query.filter_by(commercial=commercial_selected)
        
        creances = query.all()
        
        stats = {
            'count': len(creances),
            'soldees': len([c for c in creances if c.solde <= 0]),
            'montant_total': sum(c.montant for c in creances),
            'montant_solde': sum(c.solde for c in creances)
        }
    
    if request.method == 'POST':
        action = request.form.get('action')
        commercial = request.form.get('commercial')
        reason = request.form.get('reason')
        confirmation_code = request.form.get('confirmation_code')
        
        # Ici, vous pourriez implémenter la logique de réinitialisation
        # Pour l'instant, on simule l'action
        flash(f'Action {action} programmée pour {commercial}. Raison: {reason}', 'info')
        return redirect(url_for('admin_reset_creances', commercial=commercial))
    
    return render_template('admin_reset_creances.html',
                         commercial_selected=commercial_selected,
                         stats=stats,
                         confirmation_code='SOC' + datetime.now().strftime('%H%M'))

@app.route('/import-creances', methods=['GET', 'POST'])
@login_required
def import_creances():
    if current_user.role != 'admin':
        flash('Accès réservé aux administrateurs', 'error')
        return redirect(url_for('accueil'))
    
    import_results = None
    
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            try:
                # Lire le fichier
                if file.filename.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # Initialiser les compteurs
                imported = 0
                errors = 0
                ignored = 0
                
                # Traiter chaque ligne
                for _, row in df.iterrows():
                    try:
                        # Validation des données obligatoires
                        commercial = row.get('Commercial')
                        client = row.get('Client')
                        montant = row.get('Montant')
                        
                        if not commercial or not client or montant is None:
                            ignored += 1
                            continue
                        
                        # Convertir les montants
                        try:
                            montant_val = float(montant)
                            versement_val = float(row.get('Versement', 0))
                        except ValueError:
                            ignored += 1
                            continue
                        
                        # Traiter les dates
                        date_facturation_str = str(row.get('Date Facturation', ''))
                        date_echeance_str = str(row.get('Date Échéance', ''))
                        
                        try:
                            if date_facturation_str:
                                date_facturation = datetime.strptime(date_facturation_str.split()[0], '%Y-%m-%d').date()
                            else:
                                date_facturation = datetime.now().date()
                        except:
                            date_facturation = datetime.now().date()
                        
                        date_echeance = None
                        if date_echeance_str and date_echeance_str.strip():
                            try:
                                date_echeance = datetime.strptime(date_echeance_str.split()[0], '%Y-%m-%d').date()
                            except:
                                pass
                        
                        # Créer la créance
                        nouvelle_creance = Creance(
                            commercial=str(commercial),
                            client=str(client),
                            marche=str(row.get('Marché', '')),
                            montant=montant_val,
                            versement=versement_val,
                            solde=montant_val - versement_val,
                            date_facturation=date_facturation,
                            date_echeance=date_echeance,
                            commentaires=str(row.get('Commentaires', '')),
                            created_by=current_user.username
                        )
                        
                        nouvelle_creance.update_statut()
                        db.session.add(nouvelle_creance)
                        imported += 1
                        
                    except Exception as e:
                        errors += 1
                        print(f"Erreur lors de l'import ligne {_}: {e}")
                
                # Sauvegarder toutes les créances
                db.session.commit()
                
                import_results = {
                    'imported': imported,
                    'errors': errors,
                    'ignored': ignored
                }
                
                flash(f'Import terminé ! {imported} créances importées, {errors} erreurs, {ignored} lignes ignorées.', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash(f'Erreur lors de l\'import du fichier: {str(e)}', 'error')
    
    return render_template('import_creances.html', import_results=import_results)

# Gestion des erreurs
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', error=traceback.format_exc()), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# ==================== CORRECTION IMPORTANTE ====================
# UN SEUL INIT_DB, PAS DE DUPLICATION !

def init_db():
    """Initialiser la base de données"""
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        
        # Vérifier si l'administrateur existe
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Créer l'administrateur
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Créer un compte commercial exemple
            commercial = User(username='commercial', role='commercial', commercial='YAYA CAMARA')
            commercial.set_password('commercial123')
            db.session.add(commercial)
            
            # Créer un compte utilisateur exemple
            user = User(username='user', role='user')
            user.set_password('user123')
            db.session.add(user)
            
            db.session.commit()
            print("✅ Base de données initialisée avec des utilisateurs exemple:")
            print("   - admin / admin123 (administrateur)")
            print("   - commercial / commercial123 (commercial: YAYA CAMARA)")
            print("   - user / user123 (utilisateur standard)")

# ==================== UN SEUL POINT D'ENTRÉE ====================
if __name__ == '__main__':
    # Initialiser la base de données
    init_db()
    
    # PORT POUR RENDER
    port = int(os.environ.get('PORT', 5000))
    
    # Lancer l'application
    print("\n" + "="*50)
    print("SUIVI DES CRÉANCES SOCoMA")
    print("="*50)
    print(f"🚀 Serveur démarré sur: http://0.0.0.0:{port}")
    print("📂 Base de données: creances.db")
    print("👤 Compte administrateur: admin / admin123")
    print("👤 Compte commercial: commercial / commercial123")
    print("👤 Compte utilisateur: user / user123")
    print("="*50 + "\n")
    
    # IMPORTANT: debug=False pour Render (production)
    app.run(debug=False, host='0.0.0.0', port=port)