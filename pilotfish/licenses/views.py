import os
import json
from datetime import datetime
import random
from decimal import Decimal
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from Pilot_Fish.settings import EMAIL_HOST_USER
from .forms import CustomUserCreationForm  # Import correct
from django.shortcuts import render, redirect
import random
from .models import CustomUser, Robot
from .models import License, BuyOffer, SellOffer, LicenseTransaction, CustomUser
from .security_utils import generate_seed_phrase, hash_seed_phrase, generate_otp_secret, get_qr_code_url, verify_otp_code
from django.contrib.auth.forms import UserCreationForm  # À remplacer par CustomUserCreationForm si dispo
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import License, LicenseTransaction, BuyOffer, SellOffer


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.contrib import messages
from decimal import Decimal
from datetime import datetime
import os, json

from .models import License, LicenseTransaction, BuyOffer, SellOffer, Robot


@login_required
def dashboard_view(request):
    solde_data_path = os.path.join(settings.BASE_DIR, 'static', 'solde_data.json')
    solde_points = []

    try:
        with open(solde_data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
            headers = raw_data[0][0]
            heure_idx = headers.index("Heure")
            solde_idx = headers.index("Solde")

            for row in raw_data[1:]:
                data = row[0]
                heure_str = data[heure_idx]
                solde_str = data[solde_idx].replace(' ', '')
                dt = datetime.strptime(heure_str, "%Y.%m.%d %H:%M")
                timestamp = int(dt.timestamp())
                solde = float(solde_str)
                solde_points.append({"time": timestamp, "value": solde})
    except Exception as e:
        print("Erreur lecture fichier solde_data.json :", e)

    # Soumission d'une nouvelle licence
    if request.method == "POST" and request.POST.get("action") == "create_license":
        login_id = request.POST.get("login_id")
        broker = request.POST.get("broker")
        user_name = request.POST.get("user_name")
        license_type = request.POST.get("license_type")
        volume = Decimal(request.POST.get("volume"))

        if license_type == License.MICRO and not (Decimal('0.1') <= volume <= Decimal('0.9')):
            messages.error(request, "Volume invalide pour une licence Micro.")
        elif license_type == License.MACRO and not (Decimal('1') <= volume <= Decimal('100')):
            messages.error(request, "Volume invalide pour une licence Macro.")
        else:
            if license_type == License.MICRO:
                License.objects.create(
                    owner=request.user,
                    login_id=login_id,
                    broker=broker,
                    user_name=user_name,
                    license_type=license_type,
                    volume=volume,
                )
            else:
                for _ in range(int(volume)):
                    License.objects.create(
                        owner=request.user,
                        login_id=login_id,
                        broker=broker,
                        user_name=user_name,
                        license_type=license_type,
                        volume=1,
                    )
            messages.success(request, "Licence(s) ajoutée(s) avec succès.")
            return redirect("dashboard")

    # Données à afficher
    my_licenses = License.objects.filter(owner=request.user)
    my_transactions = LicenseTransaction.objects.filter(buyer=request.user)
    buy_offers = BuyOffer.objects.all()
    sell_offers = SellOffer.objects.all()
    robots = Robot.objects.all()  # Récupération des fichiers zip

    return render(request, "licenses/dashboard.html", {
        "solde_data_json": solde_points,
        "my_licenses": my_licenses,
        "my_transactions": my_transactions,
        "buy_offers": buy_offers,
        "sell_offers": sell_offers,
        "robots": robots,  # Injection dans le template
    })



@login_required
def create_license_view(request):
    if request.method == "POST":
        login_id = request.POST.get("login_id")
        broker = request.POST.get("broker")
        user_name = request.POST.get("user_name")
        license_type = request.POST.get("license_type")
        volume_str = request.POST.get("volume")

        try:
            volume = Decimal(volume_str)
        except:
            messages.error(request, "Volume invalide.")
            return redirect("create_license")

        if license_type == License.MICRO and not (Decimal('0.1') <= volume <= Decimal('0.9')):
            messages.error(request, "Pour une licence Micro, le volume doit être entre 0.1 et 0.9.")
            return redirect("create_license")

        elif license_type == License.MACRO and not (Decimal('1') <= volume <= Decimal('100')):
            messages.error(request, "Pour une licence Macro, le volume doit être entre 1 et 100.")
            return redirect("create_license")

        if license_type == License.MICRO:
            License.objects.create(
                owner=request.user,
                login_id=login_id,
                broker=broker,
                user_name=user_name,
                license_type=license_type,
                volume=volume,
                trading_account=None,
            )
        else:
            for _ in range(int(volume)):
                License.objects.create(
                    owner=request.user,
                    login_id=login_id,
                    broker=broker,
                    user_name=user_name,
                    license_type=license_type,
                    volume=1,
                    trading_account=request.POST.get("trading_account", None),
                )

        messages.success(request, "Licence(s) créée(s) avec succès !")
        return redirect("create_license")

    return render(request, "licenses/create_license.html")


def home(request):
    return render(request, "home.html")


@login_required
def market_view(request):
    offers = SellOffer.objects.exclude(user=request.user).select_related('license')
    return render(request, 'licenses/market.html', {'offers': offers})


@login_required
def buy_license_view(request, offer_id):
    offer = get_object_or_404(SellOffer.objects.select_related('license', 'user'), id=offer_id)

    if offer.user == request.user:
        messages.error(request, "Vous ne pouvez pas acheter votre propre licence.")
        return redirect('market')

    license_obj = offer.license
    previous_owner = license_obj.owner

    license_obj.owner = request.user
    license_obj.active = True
    license_obj.save()

    LicenseTransaction.objects.create(
        license=license_obj,
        buyer=request.user,
        seller=previous_owner,
        price=offer.price,
        source="USER"
    )

    offer.delete()
    messages.success(request, "Licence achetée avec succès !")
    return redirect('my_licenses')


@login_required
def sell_license_view(request):
    if request.method == 'POST':
        license_id = request.POST.get('license_id')
        price = request.POST.get('price')

        try:
            license_obj = License.objects.get(id=license_id, owner=request.user)
        except License.DoesNotExist:
            messages.error(request, "Licence introuvable ou non autorisée.")
            return redirect('my_licenses')

        if SellOffer.objects.filter(license=license_obj).exists():
            messages.error(request, "Cette licence est déjà en vente.")
            return redirect('my_licenses')

        SellOffer.objects.create(user=request.user, license=license_obj, price=price)
        messages.success(request, "Licence mise en vente.")
        return redirect('my_licenses')

    licenses = License.objects.filter(owner=request.user)
    return render(request, 'licenses/sell_license.html', {'licenses': licenses})


@login_required
def my_licenses_view(request):
    licenses = License.objects.filter(owner=request.user)
    return render(request, 'licenses/my_license.html', {'licenses': licenses})


@login_required
def investment_history_view(request):
    transactions = LicenseTransaction.objects.filter(buyer=request.user).order_by('-transaction_date')
    return render(request, 'licenses/history.html', {'transactions': transactions})


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def add_buy_offer_view(request):
    if request.method == "POST":
        login_id = request.POST.get('login_id')
        broker = request.POST.get('broker')
        user_name = request.POST.get('user_name')
        license_type = request.POST.get('license_type', 'DEMO')

        # Simple validation
        if not login_id or not broker or not user_name:
            messages.error(request, "Tous les champs sont obligatoires.")
            return render(request, "licenses/add_buy_offer.html")

        BuyOffer.objects.create(
            user=request.user,
            login_id=login_id,
            email=request.user.email,
            server=broker,
            license_type=license_type,
            fullname=user_name
        )

        messages.success(request, "Offre d'achat ajoutée avec succès.")
        return redirect('dashboard')

    # Si GET, afficher le formulaire
    return render(request, "licenses/add_buy_offer.html")


from decimal import Decimal
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import License, SellOffer

@login_required
def add_sell_offer_view(request):
    if request.method == "POST":
        license_key = request.POST.get('license_key')
        license_category = request.POST.get('license_category')  # MICRO / MACRO
        volume_str = request.POST.get('volume')
        price_str = request.POST.get('price')

        if not all([license_key, license_category, volume_str, price_str]):
            messages.error(request, "Veuillez remplir tous les champs.")
            return redirect('add_sell_offer')

        try:
            volume = Decimal(volume_str)
            price = Decimal(price_str)
        except:
            messages.error(request, "Volume et prix doivent être des nombres valides.")
            return redirect('add_sell_offer')

        try:
            license_obj = License.objects.get(key=license_key, owner=request.user)
        except License.DoesNotExist:
            messages.error(request, "Licence non trouvée ou non associée à votre compte.")
            return redirect('add_sell_offer')

        # Comparaison avec le type MICRO / MACRO
        if license_obj.license_type != license_category:
            messages.error(request, "La catégorie de licence ne correspond pas à la clé fournie.")
            return redirect('add_sell_offer')

        # Vérifie si volume correspond
        if license_obj.volume != volume:
            messages.error(request, "Le volume ne correspond pas à la licence.")
            return redirect('add_sell_offer')

        # Vérifie s’il y a déjà une offre
        if SellOffer.objects.filter(license=license_obj).exists():
            messages.error(request, "Cette licence est déjà en vente.")
            return redirect('add_sell_offer')

        # Crée l’offre de vente
        SellOffer.objects.create(user=request.user, license=license_obj, login_id=license_obj.login_id, price=price)
        messages.success(request, "Offre de vente ajoutée avec succès.")
        return redirect('dashboard')

    return render(request, 'licenses/add_sell_offer.html')



def signup_view(request):
    print(">>> signup_view appelée")
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        print(f"Données reçues dans form : {request.POST}")

        if form.is_valid():
            print("Le formulaire est valide")
            email = form.cleaned_data.get("email")
            print(f"Email récupéré depuis le formulaire : {email}")

            # Suppression de la vérification email existant (selon ta demande)
            
            user = form.save(commit=False)
            user.email = email
            user.is_active = False
            print(f"Création utilisateur non actif : {user}")

            # Générer sécurité
            seed_phrase = generate_seed_phrase()
            hashed_phrase = hash_seed_phrase(seed_phrase)
            otp_secret = generate_otp_secret()
            print(f"Seed phrase générée : {' '.join(seed_phrase)}")
            print(f"Seed phrase hashée : {hashed_phrase}")
            print(f"OTP secret généré : {otp_secret}")

            user.seed_phrase_hash = hashed_phrase
            user.otp_secret = otp_secret
            user.save()
            print(f"Utilisateur sauvegardé avec ID : {user.id}")

            # Stockage en session
            request.session['seed_phrase'] = seed_phrase
            request.session['otp_secret'] = otp_secret
            print("Seed phrase et otp_secret stockés en session")

            code = str(random.randint(100000, 999999))
            request.session['verification_code'] = code
            request.session['user_id_for_verif'] = user.id
            print(f"Code de vérification généré : {code} et stocké en session")

            # Envoi mail avec fail_silently=False pour debugger si erreur SMTP
            try:
                print(f"Envoi email à {email}...")
                send_mail(
                    "Code de vérification - Pilot Fish",
                    f"Votre code : {code}\n\nPhrase de sécurité : {' '.join(seed_phrase)}",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )
                print("Email envoyé avec succès")
                messages.success(request, "Code de vérification envoyé. Consultez votre email.")
                return redirect('verify_account')
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email : {e}")
                messages.error(request, "Erreur lors de l'envoi de l'email. Veuillez réessayer plus tard.")
                return render(request, "licenses/signup.html", {"form": form})

        else:
            print("Le formulaire est invalide, erreurs :")
            print(form.errors)
            messages.error(request, "Erreur dans le formulaire, vérifiez les informations.")
            return render(request, "licenses/signup.html", {"form": form})

    else:
        print("Méthode GET détectée, affichage du formulaire vide")
        form = CustomUserCreationForm()

    return render(request, "licenses/signup.html", {"form": form})


def verify_account_view(request):
    if request.method == "POST":
        code = request.POST.get("code")
        session_code = request.session.get('verification_code')
        user_id = request.session.get('user_id_for_verif')

        if code == session_code and user_id:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = True
            user.save()

            login(request, user)
            del request.session['verification_code']
            del request.session['user_id_for_verif']

            messages.success(request, "Compte vérifié et activé avec succès !")
            return redirect('dashboard')
        else:
            messages.error(request, "Code de vérification invalide.")

    return render(request, "licenses/verify_step.html")


@csrf_exempt
def verify_license_post(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            key = data.get("key")
            account = str(data.get("account"))
            broker = data.get("broker")
            user_name = data.get("user_name")

            license = License.objects.filter(
                key=key,
                login_id=account,
                broker=broker,
                user_name=user_name,
                active=True
            ).first()

            if license and license.is_valid():
                return JsonResponse({"status": "VALID"})
            else:
                return JsonResponse({"status": "INVALID"})
        except json.JSONDecodeError as e:
            return JsonResponse({"status": "ERROR", "message": f"JSONDecodeError: {str(e)}"})
        except Exception as e:
            return JsonResponse({"status": "ERROR", "message": str(e)})
    return JsonResponse({"status": "ERROR", "message": "Only POST method allowed"})


def verify_license(request, key):
    try:
        license = License.objects.get(key=key)
        return JsonResponse({"status": "VALID" if license.is_valid() else "EXPIRED"})
    except License.DoesNotExist:
        return JsonResponse({"status": "NOT_FOUND"})

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, "Ce compte n'est pas encore activé.")
                return redirect('login')
            login(request, user)
            messages.success(request, "Connexion réussie.")
            return redirect('dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")
    else:
        form = AuthenticationForm()

    return render(request, "licenses/login.html", {"form": form})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from licenses.models import CustomUser
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model

User = get_user_model()

def verify_account(request):
    seed_phrase = request.session.get('seed_phrase', [])
    verification_code = request.session.get('verification_code', '')
    user_id = request.session.get('user_id_for_verif')

    if not seed_phrase or not verification_code or not user_id:
        messages.error(request, "Session expirée. Veuillez recommencer l'inscription.")
        return redirect('signup')

    if request.method == 'POST':
        user_words = [request.POST.get(f'word{i}', '').strip().lower() for i in range(1, 11)]
        user_code = request.POST.get('code', '').strip()

        if user_words == seed_phrase and user_code == verification_code:
            user = get_object_or_404(User, id=user_id)
            user.is_active = True
            user.is_email_verified = True
            user.save()

            # Nettoyer la session et connecter l'utilisateur
            request.session.flush()
            login(request, user)

            messages.success(request, "✅ Votre compte a été vérifié avec succès.")
            return redirect('dashboard')

        else:
            messages.error(request, "❌ Code ou phrase de sécurité incorrecte. Veuillez réessayer.")
            # On continue vers le render du formulaire

    return render(request, 'licenses/verify_account.html')

class CustomLogoutView(LogoutView):
    next_page = 'home'
    
def logout_view(request):
    logout(request)
    return redirect('home')    

from django.http import JsonResponse

@login_required
def solde_data_view(request):
    path = os.path.join(settings.BASE_DIR, 'licenses', 'static', 'solde_data.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def forgot_password_view(request):
    if request.method == 'POST':
        words = [request.POST.get(f'word{i}', '').strip().lower() for i in range(1, 11)]

        # Recherche utilisateur par hash de phrase
        from .security_utils import hash_seed_phrase
        hashed = hash_seed_phrase(words)
        user = CustomUser.objects.filter(seed_phrase_hash=hashed).first()

        if user:
            request.session['user_id_for_reset'] = user.id
            messages.success(request, "Phrase correcte. Veuillez définir un nouveau mot de passe.")
            return redirect("set_new_password")
        else:
            messages.error(request, "❌ Phrase incorrecte. Si vous ne vous en souvenez pas, contactez le support.")
    return render(request, "licenses/forgot_password_phrase.html")

from django.contrib.auth.hashers import make_password

def set_new_password_view(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm = request.POST.get("confirm")

        if password != confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect("set_new_password")

        user_id = request.session.get("user_id_for_reset")
        user = CustomUser.objects.filter(id=user_id).first()

        if user:
            user.password = make_password(password)
            user.save()
            request.session.flush()
            messages.success(request, "Mot de passe réinitialisé avec succès. Vous pouvez vous connecter.")
            return redirect("login")
        else:
            messages.error(request, "Utilisateur non trouvé. Veuillez recommencer.")
    return render(request, "licenses/set_new_password.html")
