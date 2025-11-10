from sqlalchemy import case, desc, asc
from app import db 
from core.repositories.BaseRepository import BaseRepository 
from app.modules.comment.models import Comment, CommentVote 

class CommentRepository(BaseRepository):
    def __init__(self):
        super().__init__(Comment)

    def get_parent_comments_for_dataset(self, dataset_id: int):
        """
        Criterio de ordenación de comentarios
        1. Fijados (is_pinned = True)
        2. Más gustados (likes DESC)
        3. Menos dislikes (dislikes ASC)
        4. Más recientes (created_at DESC)
        """
        
        comments = self.model.query.filter(
            self.model.dataset_id == dataset_id,
            self.model.parent_id == None,
            self.model.is_hidden == False
        )

        pinned_priority = case(
            (self.model.is_pinned == True, 0),
            else_=1
        )
        
        ordered_comments = comments.order_by(
            asc(pinned_priority),
            desc(self.model.likes),
            asc(self.model.dislikes),
            desc(self.model.created_at)
        ).all()

        return comments

    def get_replies_for_comment(self, parent_comment_id: int):
        parent_comment = self.find_by_id(parent_comment_id)
        
        if not parent_comment or parent_comment.is_hidden:
            return []
            
        return self.model.query.filter(
            self.model.parent_id == parent_comment_id,
            self.model.is_hidden == False 
        ).order_by(
            asc(self.model.created_at)
        ).all()
    
    def get_vote_by_user(self, user_id: int, comment_id: int) -> CommentVote:
        return CommentVote.query.get((user_id, comment_id))
    
    def add_vote(self, user_id: int, comment_id: int, vote_type: int):
        vote = CommentVote(user_id=user_id, comment_id=comment_id, vote_type=vote_type)
        db.session.add(vote)
        
    def update_vote(self, vote: CommentVote, new_vote_type: int):
        vote.vote_type = new_vote_type
        
    def delete_vote(self, vote: CommentVote):
        db.session.delete(vote)