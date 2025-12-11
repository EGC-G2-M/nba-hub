# app/modules/comment/seeders.py

from app.modules.auth.models import User
from app.modules.dataset.models import DataSet
from app.modules.comment.models import Comment

from core.seeders.BaseSeeder import BaseSeeder
from datetime import datetime, timedelta

from app import db 
import click 

class CommentSeeder(BaseSeeder):

    priority = 20

    def run(self):
        
        users = User.query.all()
        all_datasets = DataSet.query.order_by(DataSet.id.desc()).all()

        if len(users) < 4:
            click.echo(click.style("ALERTA: Faltan usuarios. Saltando CommentSeeder.", fg="red"))
            return
        if len(all_datasets) < 4:
            click.echo(click.style("ALERTA: Faltan datasets. Saltando CommentSeeder.", fg="red"))
            return

        dataset_1 = all_datasets[0]
        dataset_2 = all_datasets[1]
        user_mj = users[0]
        user_ld = users[1]
        user_pg = users[2]
        user_mg = users[3]

        try:
            comment_padre = Comment(
                content="Spurs team is amazing!",
                user_id=user_mg.id,
                dataset_id=dataset_1.id,
                created_at=datetime.now() - timedelta(days=2) 
            )
            
            db.session.add(comment_padre)

            db.session.flush() 
            
            seeded_parent = comment_padre
            
            reply_1 = Comment(
                content="I agree with you, Marc!",
                user_id=user_ld.id,
                dataset_id=dataset_1.id,
                parent_id=seeded_parent.id, 
                created_at=datetime.now() - timedelta(days=1, hours=2)
            )
            db.session.add(reply_1) 
            
            reply_2 = Comment(
                content="Absolutely, one of the best teams ever.",
                user_id=user_pg.id,
                dataset_id=dataset_1.id,
                parent_id=seeded_parent.id, 
                created_at=datetime.now() - timedelta(days=1)
            )
            db.session.add(reply_2)

            reply_3 = Comment(
                content="They are the second best team,  after the Bulls :-)",
                user_id=user_mj.id,
                dataset_id=dataset_1.id,
                parent_id=seeded_parent.id, 
                created_at=datetime.now() - timedelta(hours=1)
            )
            db.session.add(reply_3)
            
            for i in range(4):
                texts = ["Great dataset!", "Very informative.", "Helped me a lot.", "Well organized data."]
                comment = Comment(
                    content=texts[i % len(texts)],
                    user_id=users[i % len(users)].id,  
                    dataset_id=dataset_2.id,
                    created_at=datetime.now() - timedelta(hours=1 + 3 * i)
                )
                db.session.add(comment) 

            for dataset in all_datasets[3:]:
                comment = Comment(
                    content="Interesting dataset, thanks for sharing!",
                    user_id=users[(dataset.id - 1) % len(users)].id,  
                    dataset_id=dataset.id,
                    created_at=datetime.now() - timedelta(hours=1 * dataset.id)
                )
                db.session.add(comment) 

            db.session.commit()
            click.echo(click.style(f"Comentarios sembrados con éxito. Total: {Comment.query.count()}", fg="green"))

        except Exception as e:
            db.session.rollback()
            click.echo(click.style(f"⚠️ ERROR AL SEMBRAR COMENTARIOS: {e}", fg="red", bold=True))
            raise