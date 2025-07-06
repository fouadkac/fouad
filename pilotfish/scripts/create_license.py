from licenses.models import License
from django.contrib.auth.models import User
from uuid import UUID

# Créer ou récupérer l'utilisateur sans mot de passe
user, created = User.objects.get_or_create(
    username="trader",
    email="trader@email.com"
)

# Créer la licence (adapte login_id et broker à ton compte réel)
license = License.objects.create(
    owner=user,
    key=UUID("3c2f963d-0c2e-4dd2-a443-00ec9e2a3056"),
    login_id="7297790",  # remplace par le bon ID
    broker="ICMarketsSC-MT5-2",  # remplace par le bon broker
    active=True
)

print("✅ Licence créée :", license)

print("✅ Licence créée :", license)
