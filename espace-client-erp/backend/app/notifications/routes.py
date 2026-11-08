from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models_erp import NotificationErp

notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/notifications")


def _notif_to_dict(n: NotificationErp) -> dict:
    return {
        "id": n.id,
        "type": n.type,
        "title": n.titre,
        "message": n.message,
        "link": n.lien,
        "is_read": n.est_lu,
        "created_at": n.created_at.isoformat() if n.created_at else None,
    }


@notifications_bp.get("")
@jwt_required()
def list_notifications():
    """4.11 Liste complète des notifications du client connecté."""
    utilisateur_id = int(get_jwt_identity())
    notifications = (
        NotificationErp.query.filter_by(utilisateur_id=utilisateur_id)
        .order_by(NotificationErp.created_at.desc())
        .all()
    )
    return jsonify(
        {
            "notifications": [_notif_to_dict(n) for n in notifications],
            "unread_count": sum(1 for n in notifications if not n.est_lu),
        }
    )


@notifications_bp.post("/<int:notification_id>/read")
@jwt_required()
def mark_read(notification_id: int):
    utilisateur_id = int(get_jwt_identity())
    notification = NotificationErp.query.filter_by(
        id=notification_id, utilisateur_id=utilisateur_id
    ).first()
    if not notification:
        return jsonify({"errors": {"general": "Notification introuvable."}}), 404

    notification.est_lu = True
    db.session.commit()
    return jsonify({"message": "Notification marquée comme lue."})


@notifications_bp.post("/read-all")
@jwt_required()
def mark_all_read():
    utilisateur_id = int(get_jwt_identity())
    NotificationErp.query.filter_by(utilisateur_id=utilisateur_id, est_lu=False).update(
        {"est_lu": True}
    )
    db.session.commit()
    return jsonify({"message": "Toutes les notifications ont été marquées comme lues."})
