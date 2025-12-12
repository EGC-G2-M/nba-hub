from app.modules.auth.models import User
from app.modules.dataset.models import DataSet
from app.modules.comment.models import Comment, CommentVote

from core.seeders.BaseSeeder import BaseSeeder
from datetime import datetime, timedelta
import click
from app import db


class CommentSeeder(BaseSeeder):
    priority = 20
    
    def run(self):
        RANDOM_COMMENTS = [ 
            "This dataset is very comprehensive, thank you for sharing!",
            "The data organization is nice.",
            "It has been extremely helpful for my final project.",
            "Interesting, although I'd like to see more documentation about the source.",
            "A great contribution to the community. Congratulations!",
            "Simple and effective. Just what I was looking for.",
            "Are there plans to update this data soon?",
            "Thanks for sharing! It saved me a lot of time.",
            "Very well visualized. Excellent data cleaning work.",
        ]

        RANDOM_VOTES = [1, -1, 0, 1, 1, -1, 0, 1, -1, 0]


        users = User.query.all()
        all_datasets = DataSet.query.order_by(DataSet.id.desc()).all()

        if len(users) < 4:
            click.echo(click.style("ALERTA: Faltan usuarios (min 4). Saltando CommentSeeder.", fg="red"))
            return
        if len(all_datasets) < 4:
            click.echo(click.style("ALERTA: Faltan datasets (min 4). Saltando CommentSeeder.", fg="red"))
            return

        dataset_1 = all_datasets[0]  # Dataset para ejemplo fijo con respuestas
        dataset_2 = all_datasets[1]  # Dataset para ejemplo fijo con múltiples comentarios
        #dataset_3 = all_datasets[2]  Dataset para ejemplo fijo sin comentarios

        user_mj = users[0]
        user_ld = users[1]
        user_pg = users[2]
        user_mg = users[3]
        all_users = users

        try:
            db.session.query(CommentVote).delete()
            db.session.query(Comment).delete() 
            db.session.commit()
        except Exception as e:
            click.echo(click.style(f"⚠️ ERROR AL LIMPIAR VOTOS/COMENTARIOS: {e}", fg="red", bold=True))
            db.session.rollback()
            raise

        try:
            # 1. DATASET WITH ONE COMMENT WITH REPLIES
            parent_comment = Comment(
                content="Spurs team is amazing!",
                user_id=user_mg.id,
                dataset_id=dataset_1.id,
                created_at=datetime.now() - timedelta(days=2),
                is_pinned=True
            )
            db.session.add(parent_comment)
            db.session.flush()
            vote_ld = CommentVote(user_id=user_ld.id, comment_id=parent_comment.id, vote_type=1)
            vote_pg = CommentVote(user_id=user_pg.id, comment_id=parent_comment.id, vote_type=1)
            vote_mj = CommentVote(user_id=user_mj.id, comment_id=parent_comment.id, vote_type=-1)
            db.session.add_all([vote_ld, vote_pg, vote_mj])
            parent_comment.likes = 2
            parent_comment.dislikes = 1
            seeded_parent = parent_comment
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
                content="They are the second best team, after the Bulls :-)",
                user_id=user_mj.id,
                dataset_id=dataset_1.id,
                parent_id=seeded_parent.id,
                created_at=datetime.now() - timedelta(hours=1)
            )
            db.session.add(reply_3)

            # 2. DATASET WITH MULTIPLE COMMENTS
            comments_d2 = []
            for i in range(4):
                texts = ["Great dataset!", "Very informative.", "Helped me a lot.", "Well organized data."]
                comment = Comment(
                    content=texts[i % len(texts)],
                    user_id=users[i % len(users)].id,
                    dataset_id=dataset_2.id,
                    created_at=datetime.now() - timedelta(hours=1 + 3 * i)
                )
                db.session.add(comment)
                comments_d2.append(comment)
            db.session.flush()
            first_comment_d2 = comments_d2[0]
            first_comment_d2.is_pinned = True
            vote_mg_first_comment = CommentVote(user_id=user_mg.id, comment_id=first_comment_d2.id, vote_type=1)
            vote_pg_first_comment = CommentVote(user_id=user_pg.id, comment_id=first_comment_d2.id, vote_type=1)
            vote_ld_first_comment = CommentVote(user_id=user_ld.id, comment_id=first_comment_d2.id, vote_type=-1)
            db.session.add_all([vote_mg_first_comment, vote_pg_first_comment, vote_ld_first_comment])
            first_comment_d2.likes = 2
            first_comment_d2.dislikes = 1

            second_comment_d2 = comments_d2[2]
            vote_mg_second_comment = CommentVote(user_id=user_mg.id, comment_id=second_comment_d2.id, vote_type=1)
            vote_pg_second_comment = CommentVote(user_id=user_pg.id, comment_id=second_comment_d2.id, vote_type=1)
            vote_ld_second_comment = CommentVote(user_id=user_ld.id, comment_id=second_comment_d2.id, vote_type=1)
            vote_mj_second_comment = CommentVote(user_id=user_mj.id, comment_id=second_comment_d2.id, vote_type=1)   
            db.session.add_all([vote_mg_second_comment, vote_pg_second_comment, vote_ld_second_comment, 
                                vote_mj_second_comment])
            
            second_comment_d2.likes = 4

            # 3. ONE DATASET WITHOUT COMMENTS 
            # all_datasets[2] remains without comments

            # 4. COMMENTS AND VOTES FOR OTHER DATASETS (Starting from index 3)            
            for i, dataset in enumerate(all_datasets[3:]): 
                content = RANDOM_COMMENTS[dataset.id % len(RANDOM_COMMENTS)]
                is_pinned = (dataset.id % 3 == 0) 
                user_id_creator = users[dataset.id % len(users)].id 

                comment = Comment(
                    content=content,
                    user_id=user_id_creator, 
                    dataset_id=dataset.id,
                    created_at=datetime.now() - timedelta(hours = 2 * dataset.id),
                    is_pinned=is_pinned
                )
                db.session.add(comment) 
                db.session.flush() 
                
                new_votes = []
                comment_likes = 0
                comment_dislikes = 0
                
                for j, user in enumerate(all_users):
                    vote_type = RANDOM_VOTES[(i + j) % len(RANDOM_VOTES)]
                    
                    if vote_type == 1:
                        new_votes.append(CommentVote(user_id=user.id, comment_id=comment.id, vote_type=1))
                        comment_likes += 1
                    elif vote_type == -1:
                        new_votes.append(CommentVote(user_id=user.id, comment_id=comment.id, vote_type=-1))
                        comment_dislikes += 1

                db.session.add_all(new_votes)
                
                comment.likes = comment_likes
                comment.dislikes = comment_dislikes

            db.session.commit()
            click.echo(click.style(
                f"Comentarios y Votos sembrados con éxito. Total Comentarios: {Comment.query.count()}. Total Votos: {
                    CommentVote.query.count()}", fg="green"))

        except Exception as e:
            db.session.rollback()
            click.echo(click.style(f"⚠️ ERROR AL SEMBRAR COMENTARIOS Y VOTOS: {e}", fg="red", bold=True))
            raise