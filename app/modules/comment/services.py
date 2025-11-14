from app import db 
from core.services.BaseService import BaseService 
from app.modules.comment.models import Comment, CommentVote
from app.modules.comment.repositories import CommentRepository 

VOTE_LIKE = 1
VOTE_DISLIKE = -1


class CommentService(BaseService):
    
    def __init__(self, repository: CommentRepository = None):
        repo = repository if repository is not None else CommentRepository()
        super().__init__(repo)
        self.comment_repository: CommentRepository = repo

    def get_parent_comments_for_dataset(self, dataset_id: int) -> int:
        return self.comment_repository.get_parent_comments_for_dataset(dataset_id)

    def get_parent_comments_for_dataset_count(self, dataset_id: int) -> int:
        comments = self.comment_repository.get_parent_comments_for_dataset(dataset_id)
        return len(comments)

    def get_replies_for_comment(self, parent_comment_id: int) -> int:
        return self.comment_repository.get_replies_for_comment(parent_comment_id)
        
    
    def create_comment(self, dataset_id: int, user_id: int, content: str, parent_id: int = None) -> Comment:        
        if not content or len(content) > 1000:
            raise ValueError("Content length is invalid or empty.")

        new_comment = Comment(
            dataset_id=dataset_id,
            user_id=user_id,
            content=content,
            parent_id=parent_id #la fecha y demás campos ya se establecen por defecto según el model 
        )
        db.session.add(new_comment)
        db.session.commit()
        return new_comment
        
    def delete_comment(self, comment_id: int, current_user_id: int, is_admin: bool = False):
        comment = self.comment_repository.find_by_id(comment_id)
        
        if not comment:
            raise ValueError("Comment not found.")
            
        if comment.user_id != current_user_id and not is_admin:
            raise PermissionError("You do not have permission to delete this comment.")
            
        if comment.parent_id is None:
            comment.replies.delete()
        
        comment.votes.delete()

        db.session.delete(comment)
        db.session.commit()

    
    def toggle_vote(self, comment_id: int, user_id: int, new_vote_type: int) -> Comment:
        if new_vote_type not in [VOTE_LIKE, VOTE_DISLIKE]:
            raise ValueError("Invalid vote type.")

        comment = self.comment_repository.find_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found.")

        existing_vote = self.comment_repository.get_vote_by_user(user_id, comment_id)
        old_vote_type = 0 

        if existing_vote:
            old_vote_type = existing_vote.vote_type
            
            if old_vote_type == new_vote_type:
                self.comment_repository.delete_vote(existing_vote)
                new_vote_type = 0  # para eliminar voto y no sumarlo dos veces
            else:
                self.comment_repository.update_vote(existing_vote, new_vote_type)
        else:
            self.comment_repository.add_vote(user_id, comment_id, new_vote_type)

        self._recalculate_votes(comment, old_vote_type, new_vote_type)
        db.session.commit()
        return comment
    
    def _recalculate_votes(self, comment: Comment, old_vote: int, new_vote: int):
        if old_vote in [VOTE_LIKE, VOTE_DISLIKE]:
            self._remove_vote(comment, old_vote)

        if new_vote in [VOTE_LIKE, VOTE_DISLIKE]:
            self._add_vote(comment, new_vote)

    def _add_vote(self, comment: Comment, vote_type: int):
        if vote_type == VOTE_LIKE:
            comment.likes += 1
        elif vote_type == VOTE_DISLIKE:
            comment.dislikes += 1
        db.session.add(comment)

    def _remove_vote(self, comment: Comment, vote_type: int):
        if vote_type == VOTE_LIKE:
            comment.likes = max(0, comment.likes - 1)
        elif vote_type == VOTE_DISLIKE:
            comment.dislikes = max(0, comment.dislikes - 1)
        db.session.add(comment)

    def toggle_pin(self, comment_id: int, pin: bool) -> Comment:
        comment = self.comment_repository.find_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found.")
            
        if comment.parent_id is not None and pin is True:
            raise ValueError("Only parent comments can be pinned.")

        if pin is True:
            comment.is_hidden = False 
            comment.is_reported = False 

        comment.is_pinned = pin
        db.session.add(comment) 
        db.session.commit()
        return comment
        
    def toggle_report(self, comment_id: int, reported: bool) -> Comment:
        comment = self.comment_repository.find_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found.")
            
        comment.is_reported = reported
        
        if reported is True:
            comment.is_pinned = False
        
        db.session.add(comment) 
        db.session.commit()
        return comment
        
    def toggle_hide(self, comment_id: int, hidden: bool) -> Comment:
        comment = self.comment_repository.find_by_id(comment_id)
        if not comment:
            raise ValueError("Comment not found.")

        comment.is_hidden = hidden
        
        if hidden is True:
            comment.is_pinned = False
        
        db.session.add(comment) 
        db.session.commit()
        return comment