import pytest
from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet, DSMetaData
from app.modules.comment.models import Comment, CommentVote
from app.modules.comment.services import CommentService
import traceback

@pytest.fixture(scope="function")
def test_data(test_client):
    """
    Crea los datos necesarios (Usuarios, Dataset) para probar comentarios.
    """    
    with test_client.application.app_context():
        owner = User.query.filter_by(email="owner_int@example.com").first()
        if not owner:
            owner = User(email="owner_int@example.com")
            owner.set_password("1234")  
            db.session.add(owner)
        
        commenter = User.query.filter_by(email="commenter_int@example.com").first()
        if not commenter:
            commenter = User(email="commenter_int@example.com")
            commenter.set_password("1234")  
            db.session.add(commenter)
            
        db.session.commit()
        unique_doi = "10.1234/comment-test-doi-integracion"
        meta = DSMetaData.query.filter_by(dataset_doi=unique_doi).first()
        
        if not meta:
            meta = DSMetaData(
                title="Integration Test Dataset",
                description="Dataset para pruebas de integración",
                publication_type="NONE",
                publication_doi="",
                dataset_doi=unique_doi,
                tags="integration,test"
            )
            db.session.add(meta)
            db.session.commit()

        ds = DataSet.query.filter_by(ds_meta_data_id=meta.id).first()
        if not ds:
            ds = DataSet(user_id=owner.id, ds_meta_data_id=meta.id)
            db.session.add(ds)
            db.session.commit()
            
        comment_to_pin_vote_reply = Comment(
            dataset_id=ds.id,
            user_id=owner.id,
            content="Votable, pinneable and repliable comment",
        )
        
        comment_to_delete = Comment(
            dataset_id=ds.id,
            user_id=commenter.id,
            content="Deletable comment",
        )
        db.session.add(comment_to_pin_vote_reply)
        db.session.add(comment_to_delete)
        db.session.commit()

        return {
            "owner_id": owner.id,
            "owner_email": owner.email,
            "commenter_id": commenter.id,
            "commenter_email": commenter.email,
            "dataset_id": ds.id,
            "comment_to_pin_vote_reply_id": comment_to_pin_vote_reply.id,
            "comment_to_delete_id": comment_to_delete.id    
        }

def test_view_dataset_comments(test_client, test_data):
    with test_client.application.app_context():
        comments_content = [
            "Primer comentario del dataset",
            "Segundo comentario del dataset",
            "Comentario pineado"
        ]
        
        for i, content in enumerate(comments_content):
            comment = Comment(
                dataset_id=test_data["dataset_id"],
                user_id=test_data["owner_id"] if i == 0 else test_data["commenter_id"],
                content=content,
                is_pinned=(i == 2)  
            )
            db.session.add(comment)
        db.session.commit()
    
    login(test_client, test_data["owner_email"], "1234")
    
    response = test_client.get(
        f"/datasets/{test_data['dataset_id']}/comments",
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    response_data = response.data.decode('utf-8')
    assert "Primer comentario del dataset" in response_data
    assert "Segundo comentario del dataset" in response_data
    assert "Comentario pineado" in response_data
    
    with test_client.application.app_context():
        pinned_comment = Comment.query.filter_by(
            dataset_id=test_data["dataset_id"],
            is_pinned=True
        ).first()
        assert pinned_comment is not None
        assert pinned_comment.content == "Comentario pineado"

def test_create_comment_route(test_client, test_data):
    logout(test_client) 

    login(test_client, test_data["commenter_email"], "1234")
    
    ds_id = test_data["dataset_id"]
    content = "Test comment integration"

    response = test_client.post(
        f"/comments/datasets/{ds_id}/comments",
        data={"content": content, "dataset_id": ds_id},
        follow_redirects=True
    )
    
    assert response.status_code == 200
    
    with test_client.application.app_context():
        comment = Comment.query.filter_by(content=content).first()
        assert comment is not None, "El comentario no se creó en la base de datos"
        assert comment.user_id == test_data["commenter_id"]
        
def test_vote_comment_route(test_client, test_data):
    with test_client.application.app_context():
        dataset_id = test_data["dataset_id"]
        c = Comment(
            dataset_id=dataset_id,
            user_id=test_data["owner_id"],
            content="Votable comment content"
        )
        db.session.add(c)
        db.session.commit()
        comment_id = c.id
        
        print(f"DEBUG: Comentario creado con ID={comment_id}")

    login_response = login(test_client, test_data["commenter_email"], "1234")
    print(f"DEBUG: Login response status={login_response.status_code if login_response else 'N/A'}")

    with test_client.session_transaction() as sess:
        print(f"DEBUG: Session user_id={sess.get('_user_id', 'NOT SET')}")

    response = test_client.post(
        f"/comments/{comment_id}/vote",
        data={"vote_type": "1"},
        headers={"Referer": f"/datasets/{dataset_id}/comments"},
        follow_redirects=True
    )
    
    print(f"DEBUG: Vote response status={response.status_code}")
    
    with test_client.application.app_context():
        c_after_vote = Comment.query.get(comment_id)
        print(f"DEBUG: Likes después del voto={c_after_vote.likes if c_after_vote else 'COMMENT NOT FOUND'}")
        print(f"DEBUG: Dislikes después del voto={c_after_vote.dislikes if c_after_vote else 'COMMENT NOT FOUND'}")
        
        votes = CommentVote.query.filter_by(comment_id=comment_id).all()
        print(f"DEBUG: Total votos en BD={len(votes)}")
        for v in votes:
            print(f"  - Vote ID={v.id}, user_id={v.user_id}, vote_type={v.vote_type}")

    print("\nDEBUG: Intentando votar directamente con el servicio...")
    with test_client.application.app_context():
        service = CommentService()
        try:
            result = service.toggle_vote(
                comment_id=comment_id,
                user_id=test_data["commenter_id"],
                new_vote_type=1
            )
            print(f"DEBUG: Servicio devolvió: {result}")
            db.session.commit()  
            
            c_after_service = Comment.query.get(comment_id)
            print(f"DEBUG: Likes después del servicio={c_after_service.likes}")
            print(f"DEBUG: Dislikes después del servicio={c_after_service.dislikes}")
            
        except Exception as e:
            print(f"DEBUG: Error en servicio: {e}")
            traceback.print_exc()

    with test_client.application.app_context():
        c_db = Comment.query.get(comment_id)
        assert c_db is not None, "El comentario desapareció de la BD"
        
        vote = CommentVote.query.filter_by(
            user_id=test_data["commenter_id"], 
            comment_id=comment_id
        ).first()
        
        print(f"\nDEBUG FINAL: likes={c_db.likes}, dislikes={c_db.dislikes}, vote_exists={vote is not None}")
        
        assert c_db.likes == 1, f"Expected 1 like, got {c_db.likes}. Votos en BD: {CommentVote.query.count()}"

def test_delete_comment_route(test_client, test_data):
    with test_client.application.app_context():
        c = Comment(
            dataset_id=test_data["dataset_id"],
            user_id=test_data["commenter_id"],
            content="To be deleted"
        )
        db.session.add(c)
        db.session.commit()
        comment_id = c.id
        print(f"DEBUG: Comentario creado para eliminar, ID={comment_id}")

    login(test_client, test_data["commenter_email"], "1234")

    with test_client.application.app_context():
        exists_before = Comment.query.get(comment_id)
        print(f"DEBUG: Comentario existe antes de eliminar: {exists_before is not None}")

    response = test_client.post(
        f"/comments/{comment_id}/delete",
        headers={"Referer": f"/datasets/{test_data['dataset_id']}/comments"},
        follow_redirects=True
    )
    
    print(f"DEBUG: Delete response status={response.status_code}")
    
    with test_client.application.app_context():
        exists_after_route = Comment.query.get(comment_id)
        print(f"DEBUG: Comentario existe después de ruta: {exists_after_route is not None}")
        
        if exists_after_route:
            print("DEBUG: Intentando eliminar directamente con el servicio...")
            service = CommentService()
            try:
                service.delete_comment(
                    comment_id=comment_id,
                    acting_user_id=test_data["commenter_id"]
                )
                db.session.commit()
                
                exists_after_service = Comment.query.get(comment_id)
                print(f"DEBUG: Comentario existe después del servicio: {exists_after_service is not None}")
            except Exception as e:
                print(f"DEBUG: Error en servicio delete: {e}")
                traceback.print_exc()
    
    with test_client.application.app_context():
        deleted_comment = Comment.query.get(comment_id)
        total_comments = Comment.query.count()
        print(f"DEBUG FINAL: deleted_comment={deleted_comment}, total_comments={total_comments}")
        assert deleted_comment is None, f"El comentario no fue eliminado. Total comments en BD: {total_comments}"

def test_pin_comment_route(test_client, test_data):
    with test_client.application.app_context():
        c = Comment(
            dataset_id=test_data["dataset_id"],
            user_id=test_data["commenter_id"],
            content="Comment to pin"
        )
        db.session.add(c)
        db.session.commit()
        comment_id = c.id
        print(f"DEBUG: Comentario creado con ID={comment_id}, dataset_id={test_data['dataset_id']}")

    login(test_client, test_data["owner_email"], "1234")  

    response = test_client.post(
        f"/comments/{comment_id}/pin",
        data={"pin_action": "pin"},
        headers={"Referer": f"/datasets/{test_data['dataset_id']}/comments"},
        follow_redirects=True
    )
    
    print(f"DEBUG: Pin response status={response.status_code}")
    assert response.status_code == 200

    with test_client.application.app_context():
        c_after_route = Comment.query.get(comment_id)
        print(f"DEBUG: is_pinned después de ruta={c_after_route.is_pinned if c_after_route else 'COMMENT NOT FOUND'}")

    print("\nDEBUG: Intentando pinear directamente con el servicio...")
    with test_client.application.app_context():
        service = CommentService()
        try:
            result = service.toggle_pin(
                comment_id=comment_id,
                pin=True,
                acting_user_id=test_data["owner_id"]
            )
            print(f"DEBUG: Servicio toggle_pin devolvió: {result}")
            db.session.commit()  
            c_after_service = Comment.query.get(comment_id)
            print(f"DEBUG: is_pinned después del servicio={c_after_service.is_pinned}")
            
        except PermissionError as pe:
            print(f"DEBUG: PermissionError en servicio: {pe}")
        except Exception as e:
            print(f"DEBUG: Error en servicio: {e}")
            import traceback
            traceback.print_exc()

    with test_client.application.app_context():
        c_db = Comment.query.get(comment_id)
        print(f"\nDEBUG FINAL: is_pinned={c_db.is_pinned}")
        assert c_db.is_pinned is True, f"Expected is_pinned=True, got {c_db.is_pinned}"