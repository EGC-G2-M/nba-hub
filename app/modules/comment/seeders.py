from app.modules.auth.models import User
from app.modules.dataset.models import DataSet
from app.modules.comment.models import Comment

from core.seeders.BaseSeeder import BaseSeeder
from datetime import datetime, timedelta

class CommentSeeder(BaseSeeder):

    priority = 10 

    def run(self):
        users = User.query.all()
        all_datasets = DataSet.query.order_by(DataSet.id.desc()).all()
        dataset_1 = all_datasets[0]  # Cogemos el dataset más reciente
        dataset_2 = all_datasets[1]  # Cogemos los 2 últimos datasets, que son los que aparecen mas arriba

        user_mj = users[0] # Michael Jordan
        user_ld = users[1] # Luka Doncic
        user_pg = users[2] # Pau Gasol
        user_mg = users[3] # Marc Gasol

        comments_to_seed = []

        # Dataset 1: 1 comentario con 4 respuestas
        comment_with_replies = Comment(
            content="Spurs team is amazing!",
            user_id=user_mg.id,
            dataset_id=dataset_1.id,
            created_at=datetime.now() - timedelta(days=2) 
        )
        
        seeded_parent = self.seed([comment_with_replies])[0]

        reply_1 = Comment(
            content="I agree with you, Marc!",
            user_id=user_ld.id,
            dataset_id=dataset_1.id,
            parent_id=seeded_parent.id, 
            created_at=datetime.now() - timedelta(days=1, hours=2)
        )
        comments_to_seed.append(reply_1)

        reply_2 = Comment(
            content="Absolutely, one of the best teams ever.",
            user_id=user_pg.id,
            dataset_id=dataset_1.id,
            parent_id=seeded_parent.id, 
            created_at=datetime.now() - timedelta(days=1)
        )
        comments_to_seed.append(reply_2)

        reply_3 = Comment(
            content="They are the second best team,  after the Bulls :-)",
            user_id=user_mj.id,
            dataset_id=dataset_1.id,
            parent_id=seeded_parent.id, 
            created_at=datetime.now() - timedelta(hours=1)
        )
        comments_to_seed.append(reply_3)

        # Dataset 2: 4 comentarios independientes
        for i in range(4):
            texts = ["Great dataset!", "Very informative.", "Helped me a lot.", "Well organized data."]
            comment = Comment(
                content=texts[i % len(texts)],
                user_id=users[i % len(users)].id,  
                dataset_id=dataset_2.id,
                created_at=datetime.now() - timedelta(hours=1 + 3 * i)
            )
            comments_to_seed.append(comment)

        # 1 dataset sin comentarios, el resto de datasets: 1 comentario cada uno
        for dataset in all_datasets[3:]:
            comment = Comment(
                content="Interesting dataset, thanks for sharing!",
                user_id=users[(dataset.id - 1) % len(users)].id,  
                dataset_id=dataset.id,
                created_at=datetime.now() - timedelta(hours=1 * dataset.id)
            )
            comments_to_seed.append(comment)

        self.seed(comments_to_seed)