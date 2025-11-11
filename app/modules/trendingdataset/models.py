from app import db


class Trendingdataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f'Trendingdataset<{self.id}>'
