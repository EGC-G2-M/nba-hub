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

@comment_bp.route("/datasets/<int:dataset_id>/comments", methods=["POST"])
@login_required
def create_comment(dataset_id):    
    form = CommentForm()
    form.dataset_id.data = dataset_id
    
    redirect_url = url_for("public.index")
    if dataset_id and dataset_service.find_by_id(dataset_id):
        redirect_url = url_for('dataset.view_all_comments_of_dataset', dataset_id=dataset_id)

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
    redirect_url = url_for("public.index")
    try:
        comment = comment_service.get_comment(comment_id)
        if comment:
            dataset_id_temp = comment.dataset_id 
            comment_service.delete_comment(
                comment_id=comment_id,
                acting_user_id=current_user.id 
            )
            flash("Comment deleted successfully", "success")
        else:
            flash("Comment not found", "danger")

    except Exception as e:
        flash(f"Error deleting comment: {e}", "danger")
    return redirect(request.referrer or url_for('main.index'))


@comment_bp.route("/<int:comment_id>/vote", methods=["POST"])
@login_required
def toggle_vote(comment_id):
    vote_type = int(request.form.get('vote_type'))
    
    if vote_type not in [VOTE_LIKE, VOTE_DISLIKE]:
        raise BadRequest("Invalid vote type provided.")

    try:
        updated_comment = comment_service.toggle_vote(
            comment_id=comment_id,
            user_id=current_user.id,
            new_vote_type=vote_type
        )
        flash("Vote updated successfully", "success") 

    except ValueError:
        flash("Invalid vote", "danger")
    except Exception as e:
        flash(f"Error voting: {str(e)}", "danger")

    return redirect(request.referrer)

@comment_bp.app_template_filter('check_vote')
def check_vote_filter(comment, user):
    """
    Filtro para usar en HTML: {{ comment | check_vote(current_user) }}
    Devuelve: 1 (Like), -1 (Dislike) o 0 (Nada)
    """
    if not user or not user.is_authenticated:
        return 0
        
    if hasattr(comment, 'votes'):
        for vote in comment.votes:
            if vote.user_id == user.id:
                return vote.vote_type
            
    return 0

# AUTOR
@comment_bp.route("/<int:comment_id>/pin", methods=["POST"])
@login_required
def toggle_pin(comment_id):
    try:
        action = request.form.get('pin_action', 'pin')
        should_pin = (action == 'pin')

        comment_service.toggle_pin(
            comment_id=comment_id,
            pin=should_pin,
            acting_user_id=current_user.id
        )
        
        msg = "Comment pinned" if should_pin else "Comment unpinned"
        flash(msg, "success")

    except PermissionError:
        flash("Only the dataset owner can pin comments", "danger")
    except Exception as e:
        flash(f"Error pinning comment: {str(e)}", "danger")

    return redirect(request.referrer)