import random
import hashlib
import pyotp # type: ignore

WORD_LIST = [
    "ability", "access", "account", "action", "active", "actor", "actual", "adapt", "addict", "adjust",
    "admit", "adopt", "adult", "affair", "affect", "afford", "afraid", "agency", "agenda", "agent", "agree",
    "ahead", "alarm", "album", "alert", "alien", "align", "alive", "allow", "alone", "along", "alter", "amend",
    "anger", "angle", "angry", "anime", "annual", "answer", "anyone", "anyway", "appeal", "appear", "apple",
    "apply", "appoint", "arena", "argue", "arise", "armor", "around", "arrive", "artist", "aspect", "assess",
    "assign", "assist", "assume", "attach", "attack", "attain", "attend", "author", "avenue", "award", "aware",
    "awful", "backup", "badge", "baker", "balance", "banal", "banker", "barely", "barrel", "basic", "basis",
    "beach", "beacon", "become", "before", "begin", "behave", "behind", "belief", "belong", "below", "benefit", 
    "beside", "betray", "better", "beyond", "binary", "bishop", "bitter", "blame", "blank", "blast", "blend", 
    "bless", "blind", "blink", "block", "blood", "bloom", "blow", "board", "boast", "bonus", "boost", "border", 
    "bother", "bottle", "bottom", "bounce", "bound", "brain", "brave", "bread", "break", "breathe", "brick", 
    "brief", "bright", "bring", "broad", "broker", "budget", "buffer", "build", "bullet", "burden", "burn", 
    "burst", "buyer", "cable", "calculate", "camera", "campus", "cancel", "cancer", "cannot", "canvas", "carbon", 
    "career", "carpet", "cartoon", "casual", "cause", "celebrity", "center", "chance", "change", "charge", "chase",
    "cheap", "check", "cheese", "choose", "circle", "claim", "clash", "class", "clean", "clear", "clerk", 
    "click", "client", "climb", "clinic", "clock", "close", "cloud", "clue", "coach", "coast", "collect", "column", 
    "combat", "come", "comment", "commit", "common", "company", "compare", "comply", "confirm", "connect", 
    "consent", "contest", "context", "control", "convert", "copy", "corner", "correct", "cost", "cotton", 
    "council", "course", "cover", "crack", "craft", "crash", "create", "credit", "crew", "crisis", "critic", 
    "cross", "crowd", "crucial", "crystal", "culture", "curious", "custom", "cycle", "daily", "damage", "danger", 
    "dark", "data", "dealer", "debate", "debt", "decade", "decide", "deck", "declare", "decline", "default", 
    "defeat", "defend", "define", "delay", "delete", "deliver", "demand", "deny", "depart", "depend", "deploy", 
    "deposit", "depth", "desert", "design", "desire", "desk", "detail", "detect", "device", "devote", "differ", 
    "dinner", "direct", "dirty", "disable", "disco", "discuss", "disease", "display", "dispute", "distance", 
    "divide", "doctor", "document", "domain", "donate", "double", "draft", "drama", "draw", "dream", "dress", 
    "drift", "drink", "drive", "drop", "dry", "duty", "early", "earn", "earth", "easily", "effect", "effort", 
    "eight", "either", "elder", "elect", "element", "elite", "else", "email", "embark", "embody", "emerge", 
    "emotion", "employ", "enable", "encore", "enemy", "energy", "engage", "engine", "enjoy", "enough", "enter", 
    "entire", "entry", "equal", "equity", "escape", "essay", "essence", "estate", "ethic", "ethnic", "evade", 
    "evening", "event", "every", "evil", "evolve", "exact", "exam", "except", "exchange", "excite", "execute", 
    "exercise", "exhibit", "expand", "expect", "expert", "expire", "explain", "explore", "express", "extend", 
    "extra", "fabric", "face", "factor", "fade", "fail", "faint", "fair", "faith", "fall", "false", "fame", 
    "family", "famous", "fancy", "fantasy", "farmer", "fashion", "fast", "father", "fault", "favor", "fear", 
    "feature", "federal", "feel", "fellow", "fence", "fever", "field", "fight", "figure", "file", "fill", "film", 
    "filter", "final", "finance", "find", "fine", "finger", "finish", "fire", "firm", "first", "fiscal", "fish", 
    "fix", "flag", "flame", "flash", "flat", "flavor", "fleet", "flex", "flight", "flip", "float", "floor", "flow", 
    "fluid", "focus", "fold", "follow", "food", "foot", "force", "forest", "forget", "form", "formal", "format", 
    "former", "fortune", "forum", "found", "frame", "free", "fresh", "friend", "front", "fuel", "fully", "function", 
    "fund", "funny", "future"
    # (il y a encore plusieurs centaines à ajouter — dites-moi si vous souhaitez un fichier complet)
]


def generate_otp_secret():
    return pyotp.random_base32()

def generate_seed_phrase():
    return random.sample(WORD_LIST, 10)

def hash_seed_phrase(phrase_list):
    phrase = ' '.join(phrase_list).lower()
    return hashlib.sha256(phrase.encode()).hexdigest()

def generate_otp_secret():
    return pyotp.random_base32()

def get_qr_code_url(user, otp_secret):
    totp = pyotp.TOTP(otp_secret)
    return totp.provisioning_uri(name=user.email, issuer_name="PilotFish")

def verify_otp_code(otp_secret, code):
    return pyotp.TOTP(otp_secret).verify(code)
