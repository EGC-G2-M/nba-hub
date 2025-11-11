from functools import wraps 
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
        is_admin = getattr(current_user, 'is_admin', True) 
        if not current_user.is_authenticated or not is_admin:
            return jsonify({"message": "Forbidden: Administrator access required."}), 403
        return f(*args, **kwargs)
    return decorated_function

# RUTAS DE USUARIO 
@comment_bp.route("/create", methods=["POST"])
@login_required
def create_comment():    
    form = CommentForm()
    dataset_id = form.dataset_id.data 
    
    redirect_url = url_for("public.index")
    if dataset_id and dataset_service.find_by_id(dataset_id):
        redirect_url = url_for("dataset.subdomain_index", doi=dataset_service.find_by_id(dataset_id).doi)

    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data and form.parent_id.data.isdigit() else None
        try:
            comment_service.create_comment(
                dataset_id=dataset_id,
                user_id=current_user.id,
                content=form.content.data,
                parent_id=parent_id
            )
            flash("Comment posted successfully!", "success")
        except Exception as exc:
            flash(f"Error creating comment: {exc}", "danger")

    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "danger")
                
    return redirect(redirect_url)


@comment_bp.route("/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment_route(comment_id):
    dataset_id = None
    redirect_url = url_for("public.index")

    try:
        is_admin_user = getattr(current_user, 'is_admin', True)
        
        comment = comment_service.find_by_id(comment_id)
        if not comment:
            raise NotFound("Comment not found.")

        dataset_id = comment.dataset_id

        comment_service.delete_comment(
            comment_id=comment_id, 
            current_user_id=current_user.id, 
            is_admin=is_admin_user
        )
        flash("Comment deleted successfully.", "success")
        
        dataset = dataset_service.find_by_id(dataset_id)
        if dataset and dataset.doi:
             redirect_url = url_for("dataset.subdomain_index", doi=dataset.doi)

    except (PermissionError, NotFound, ValueError) as exc:
        flash(f"Error deleting comment: {exc}", "danger")
        if dataset_id:
             dataset = dataset_service.find_by_id(dataset_id)
             if dataset and dataset.doi:
                redirect_url = url_for("dataset.subdomain_index", doi=dataset.doi)
    except Exception:
        flash("An unexpected error occurred while deleting the comment.", "danger")
        
    return redirect(redirect_url)


@comment_bp.route("/<int:comment_id>/vote", methods=["POST"])
@login_required
def toggle_vote_route(comment_id):
    data = request.get_json()
    vote_type = data.get('vote_type')
    
    if vote_type not in [VOTE_LIKE, VOTE_DISLIKE]:
        raise BadRequest("Invalid vote type provided.")

    try:
        updated_comment = comment_service.toggle_vote(
            comment_id=comment_id,
            user_id=current_user.id,
            new_vote_type=vote_type
        )
        
        return jsonify({
            "success": True,
            "likes": updated_comment.likes,
            "dislikes": updated_comment.dislikes
        }), 200

    except Exception as exc:
        return jsonify({"success": False, "message": str(exc)}), 400


# RUTAS DE ADMIN
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
            "comment": comment_serializer.serialize(updated_comment) 
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
            "comment": comment_serializer.serialize(updated_comment) 
        }), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception:
        return jsonify({"message": "Internal error"}), 500


@comment_bp.route('/<int:comment_id>/report', methods=['POST'])
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
            "comment": comment_serializer.serialize(updated_comment)
        }), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception:
        return jsonify({"message": "Internal error"}), 500