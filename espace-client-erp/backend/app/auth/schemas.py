import re
from email_validator import validate_email, EmailNotValidError

PASSWORD_MIN_LENGTH = 8
PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\da-zA-Z]).{%d,}$" % PASSWORD_MIN_LENGTH
)


class ValidationErrors(Exception):
    def __init__(self, errors: dict):
        self.errors = errors
        super().__init__(str(errors))


def validate_registration(data: dict) -> dict:
    errors = {}
    cleaned = {}

    # Email
    email = (data.get("email") or "").strip().lower()
    try:
        valid = validate_email(email, check_deliverability=False)
        cleaned["email"] = valid.normalized
    except EmailNotValidError:
        errors["email"] = "Adresse email invalide."

    # Mot de passe
    password = data.get("password") or ""
    if not PASSWORD_REGEX.match(password):
        errors["password"] = (
            "Le mot de passe doit contenir au moins 8 caractères, une majuscule, "
            "une minuscule, un chiffre et un caractère spécial."
        )
    else:
        cleaned["password"] = password

    # Confirmation
    if data.get("password_confirmation") != password:
        errors["password_confirmation"] = "Les mots de passe ne correspondent pas."

    # Nom / prénom
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    if not first_name:
        errors["first_name"] = "Le prénom est requis."
    else:
        cleaned["first_name"] = first_name

    if not last_name:
        errors["last_name"] = "Le nom est requis."
    else:
        cleaned["last_name"] = last_name

    cleaned["phone"] = (data.get("phone") or "").strip() or None

    if errors:
        raise ValidationErrors(errors)

    return cleaned


def validate_login(data: dict) -> dict:
    errors = {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email:
        errors["email"] = "L'email est requis."
    if not password:
        errors["password"] = "Le mot de passe est requis."

    if errors:
        raise ValidationErrors(errors)

    return {"email": email, "password": password}


def validate_password_change(data: dict) -> dict:
    errors = {}
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    if not current_password:
        errors["current_password"] = "Le mot de passe actuel est requis."

    if not PASSWORD_REGEX.match(new_password):
        errors["new_password"] = (
            "Le nouveau mot de passe doit contenir au moins 8 caractères, une majuscule, "
            "une minuscule, un chiffre et un caractère spécial."
        )

    if data.get("new_password_confirmation") != new_password:
        errors["new_password_confirmation"] = "Les mots de passe ne correspondent pas."

    if errors:
        raise ValidationErrors(errors)

    return {"current_password": current_password, "new_password": new_password}
