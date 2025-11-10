from flask import Blueprint, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required 
from werkzeug.exceptions import BadRequest, NotFound

from core.serialisers.serializer import Serializer 

from app.modules.comment.forms import CommentForm 
from app.modules.comment.services import CommentService, VOTE_LIKE, VOTE_DISLIKE
from app.modules.dataset.services import DataSetService 


COMMENT_SERIALIZATION_FIELDS = {
    'id': 'id',
    'dataset_id': 'dataset_id',
    'user_id': 'user_id',
    'parent_id': 'parent_id',
    'content': 'content',
    'created_at': 'created_at',
    'likes': 'likes',
    'dislikes': 'dislikes',
    'is_pinned': 'is_pinned',
    'is_hidden': 'is_hidden',
    'is_reported': 'is_reported'
}

comment_bp = Blueprint('comment', __name__, url_prefix='/comments')

comment_service = CommentService()
dataset_service = DataSetService()
comment_serializer = Serializer(serialization_fields=COMMENT_SERIALIZATION_FIELDS) 


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({"message": "Forbidden: Administrator access required."}), 403
        return f(*args, **kwargs)
    return decorated_function

# COMMENT, DELETE AND VOTE  

# MANAGE COMMENTS BY ADMIN
@comment_bp.route('/<int:comment_id>/pin', methods=['POST'])
@login_required
@admin_required
def toggle_pin_route(comment_id):
    data = request.get_json()
    pin_status = data.get('pin')
    
    if pin_status is None or not isinstance(pin_status, bool):
        return jsonify({"message": "Missing or invalid 'pin' status"}), 400

    try:
        updated_comment = comment_service.toggle_pin(comment_id, pin_status)
        return jsonify({
            "message": "Pin status updated successfully.",
            "comment": comment_serializer.to_dict(updated_comment)
        }), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception:
        return jsonify({"message": "Internal error"}), 500


@comment_bp.route('/<int:comment_id>/hide', methods=['POST'])
@login_required
@admin_required
def toggle_hide_route(comment_id):
    data = request.get_json()
    hidden_status = data.get('hidden')
    
    if hidden_status is None or not isinstance(hidden_status, bool):
        return jsonify({"message": "Missing or invalid 'hidden' status"}), 400

    try:
        updated_comment = comment_service.toggle_hide(comment_id, hidden_status)
        return jsonify({
            "message": "Hide status updated successfully. Pinned status adjusted automatically.",
            "comment": comment_serializer.to_dict(updated_comment)
        }), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception:
        return jsonify({"message": "Internal error"}), 500


@comment_bp.route('/<int:comment_id>/report_status', methods=['POST'])
@login_required
@admin_required
def toggle_report_route(comment_id):
    data = request.get_json()
    reported_status = data.get('reported')
    
    if reported_status is None or not isinstance(reported_status, bool):
        return jsonify({"message": "Missing or invalid 'reported' status"}), 400

    try:
        updated_comment = comment_service.toggle_report(comment_id, reported_status)
        return jsonify({
            "message": "Report status updated successfully. Pinned status adjusted automatically.",
            "comment": comment_serializer.to_dict(updated_comment)
        }), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception:
        return jsonify({"message": "Internal error"}), 500