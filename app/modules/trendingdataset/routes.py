from flask import render_template
from app.modules.trendingdataset import trendingdataset_bp
from app.modules.trendingdataset.services import TrendingdatasetService

trending_dataset_service = TrendingdatasetService()

@trendingdataset_bp.route('/trendingdataset', methods=['GET'])
def index():
    res = trending_dataset_service.get_top5_trending_datasets_last_30_days()
    datasets = [d[0] for d in res]
    downloads = [d[1] for d in res]
    return render_template('trendingdataset/index.html', trending_datasets=datasets, downloads=downloads)