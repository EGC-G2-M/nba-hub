from datetime import datetime, timezone

from app import db

class CommentVote(db.Model):
    __tablename__ = 'comment_vote'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), primary_key=True)
    
    # vote_type: 1 para Like, -1 para Dislike.
    vote_type = db.Column(db.Integer, nullable=False)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)

    # ATRIBUTOS
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    is_hidden = db.Column(db.Boolean, default=False)
    is_reported = db.Column(db.Boolean, default=False)

    # RELACIONES
    dataset_id = db.Column(db.Integer, db.ForeignKey('data_set.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)

    replies = db.relationship(
        'Comment', 
        backref=db.backref('parent', remote_side=[id]), 
        lazy='dynamic',
        order_by='Comment.created_at.asc()',
        primaryjoin="Comment.parent_id==Comment.id" 
    )
    
    votes = db.relationship(
        'CommentVote', 
        backref='comment', 
        lazy='dynamic'
    )


    def __repr__(self):
        return f"<Comment {self.id} on Dataset {self.dataset_id}>"