import pytest
from app import db
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSMetaData
from app.modules.comment.models import Comment, CommentVote
from app.modules.comment.services import CommentService, VOTE_LIKE, VOTE_DISLIKE

@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extiende el fixture test_client para preparar un entorno con:
    - Un usuario 'owner' (dueño del dataset).
    - Un usuario 'commenter' (quien comenta).
    - Un dataset de prueba.
    """
    with test_client.application.app_context():
        owner = User(email="owner@example.com", password="pass1234")
        commenter = User(email="commenter@example.com", password="pass1234")
        db.session.add(owner)
        db.session.add(commenter)
        db.session.commit()

        meta = DSMetaData(
            title="Dataset para Comentarios",
            description="Probando comentarios unitarios",
            publication_type="NONE",
            publication_doi="",
            dataset_doi=None,
            tags="test"
        )
        db.session.add(meta)
        db.session.commit()

        ds = DataSet(user_id=owner.id, ds_meta_data_id=meta.id)
        db.session.add(ds)
        db.session.commit()

        test_client.owner_id = owner.id
        test_client.commenter_id = commenter.id
        test_client.dataset_id = ds.id

    yield test_client


def test_service_create_comment(test_client):
    """
    Prueba que el servicio crea correctamente el comentario en la BD.
    """
    service = CommentService()
    
    content = "Este es un comentario de prueba unitaria"
    comment = service.create_comment(
        dataset_id=test_client.dataset_id,
        user_id=test_client.commenter_id,
        content=content
    )

    assert comment.id is not None
    assert comment.content == content
    assert comment.dataset_id == test_client.dataset_id
    assert comment.user_id == test_client.commenter_id
    
    from_db = Comment.query.get(comment.id)
    assert from_db is not None
    assert from_db.content == content


def test_service_vote_logic_add_like(test_client):
    """
    Prueba la lógica de añadir un LIKE usando el servicio.
    """
    service = CommentService()

    comment = service.create_comment(
        dataset_id=test_client.dataset_id,
        user_id=test_client.owner_id,
        content="Comentario para votar"
    )

    service.toggle_vote(
        comment_id=comment.id,
        user_id=test_client.commenter_id,
        new_vote_type=VOTE_LIKE
    )

    db.session.refresh(comment)
    assert comment.likes == 1
    assert comment.dislikes == 0

    vote_record = CommentVote.query.filter_by(
        user_id=test_client.commenter_id, 
        comment_id=comment.id
    ).first()
    assert vote_record is not None
    assert vote_record.vote_type == VOTE_LIKE


def test_service_vote_logic_switch_vote(test_client):
    """
    Prueba cambiar de LIKE a DISLIKE.
    """
    service = CommentService()
    comment = service.create_comment(
        dataset_id=test_client.dataset_id,
        user_id=test_client.owner_id,
        content="Comentario indeciso"
    )

    service.toggle_vote(comment.id, test_client.commenter_id, VOTE_LIKE)
    db.session.refresh(comment)
    assert comment.likes == 1

    service.toggle_vote(comment.id, test_client.commenter_id, VOTE_DISLIKE)
    db.session.refresh(comment)

    assert comment.likes == 0
    assert comment.dislikes == 1


def test_service_vote_logic_remove_vote(test_client):
    """
    Prueba quitar el voto si se repite la acción (toggle).
    """
    service = CommentService()
    comment = service.create_comment(
        dataset_id=test_client.dataset_id,
        user_id=test_client.owner_id,
        content="Comentario toggle"
    )

    service.toggle_vote(comment.id, test_client.commenter_id, VOTE_LIKE)
    db.session.refresh(comment)
    assert comment.likes == 1

    service.toggle_vote(comment.id, test_client.commenter_id, VOTE_LIKE)
    db.session.refresh(comment)
    assert comment.likes == 0
    
    vote_record = CommentVote.query.filter_by(
        user_id=test_client.commenter_id, 
        comment_id=comment.id
    ).first()
    assert vote_record is None


def test_service_pin_comment_logic(test_client):
    """
    Prueba que el dueño puede fijar (pin) un comentario.
    """
    service = CommentService()
    comment = service.create_comment(
        dataset_id=test_client.dataset_id,
        user_id=test_client.commenter_id,
        content="Comentario importante"
    )

    service.toggle_pin(
        comment_id=comment.id,
        pin=True,
        acting_user_id=test_client.owner_id
    )
    
    db.session.refresh(comment)
    assert comment.is_pinned is True

    service.toggle_pin(
        comment_id=comment.id,
        pin=False,
        acting_user_id=test_client.owner_id
    )
    db.session.refresh(comment)
    assert comment.is_pinned is False


def test_service_pin_comment_permission_denied(test_client):
    """
    Prueba que un usuario random NO puede fijar comentarios en un dataset ajeno.
    """
    service = CommentService()
    comment = service.create_comment(
        dataset_id=test_client.dataset_id,
        user_id=test_client.owner_id,
        content="Comentario normal"
    )

    with pytest.raises(PermissionError):
        service.toggle_pin(
            comment_id=comment.id,
            pin=True,
            acting_user_id=test_client.commenter_id
        )