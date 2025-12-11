import os
import shutil
from datetime import datetime, timezone

from dotenv import load_dotenv

from app.modules.auth.models import User
from app.modules.dataset.models import Author, DataSet, DSMetaData, DSMetrics, PublicationType
from app.modules.featuremodel.models import FeatureModel, FMMetaData
from app.modules.hubfile.models import Hubfile
from core.seeders.BaseSeeder import BaseSeeder


class DataSetSeeder(BaseSeeder):

    priority = 2  # Lower priority

    def run(self):
        # Retrieve users
        user1 = User.query.filter_by(email="user1@example.com").first()
        user2 = User.query.filter_by(email="user2@example.com").first()

        if not user1 or not user2:
            raise Exception("Users not found. Please seed users first.")

        # Create DSMetrics instance
        ds_metrics = DSMetrics(number_of_models="5", number_of_features="50")
        seeded_ds_metrics = self.seed([ds_metrics])[0]

        nba_datasets = [
            DSMetaData(
                deposition_id=1,  # Empezamos en 1
                title="East Regular Season Champs",
                description="Dataset about east-regular-season-champs",
                publication_type=PublicationType.SEASON,
                publication_doi="10.1234/east-regular-season-champs",
                dataset_doi="10.1234/east-regular-season-champs",
                tags="nba, east, champs",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=2,
                title="Marc Gasol Teams",
                description="Dataset about Marc-Gasol-teams",
                publication_type=PublicationType.PLAYER,
                publication_doi="10.1234/Marc-Gasol-teams",
                dataset_doi="10.1234/Marc-Gasol-teams",
                tags="nba, gasol, teams",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=3,
                title="Pau Gasol Playoffs Teams",
                description="Dataset about Pau-Gasol-playoffs-teams",
                publication_type=PublicationType.PLAYER,
                publication_doi="10.1234/Pau-Gasol-playoffs-teams",
                dataset_doi="10.1234/Pau-Gasol-playoffs-teams",
                tags="nba, gasol, playoffs",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=4,
                title="Playoffs 1996-97",
                description="Dataset about playoffs-1996-97",
                publication_type=PublicationType.PLAYOFFS,
                publication_doi="10.1234/playoffs-1996-97",
                dataset_doi="10.1234/playoffs-1996-97",
                tags="nba, playoffs, 1996",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=5,
                title="Playoffs Conference Champs",
                description="Dataset about playoffs-conference-champs",
                publication_type=PublicationType.PLAYOFFS,
                publication_doi="10.1234/playoffs-conference-champs",
                dataset_doi="10.1234/playoffs-conference-champs",
                tags="nba, playoffs, champs",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=6,
                title="Season 2024-25",
                description="Dataset about season-2024-25",
                publication_type=PublicationType.SEASON,
                publication_doi="10.1234/season-2024-25",
                dataset_doi="10.1234/season-2024-25",
                tags="nba, season, 2024",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=7,
                title="West Regular Season Champs",
                description="Dataset about west-regular-season-champs",
                publication_type=PublicationType.SEASON,
                publication_doi="10.1234/west-regular-season-champs",
                dataset_doi="10.1234/west-regular-season-champs",
                tags="nba, west, champs",
                ds_metrics_id=seeded_ds_metrics.id,
                extra_fields="Blocks per game"
            ),
            DSMetaData(
                deposition_id=8,
                title="Marc Gasol Playoffs Teams",
                description="Dataset about Marc-Gasol-playoffs-teams",
                publication_type=PublicationType.PLAYER,
                publication_doi="10.1234/Marc-Gasol-playoffs-teams",
                dataset_doi="10.1234/Marc-Gasol-playoffs-teams",
                tags="nba, gasol, playoffs",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=9,
                title="Michael Jordan Teams",
                description="Dataset about Michael-Jordan-teams",
                publication_type=PublicationType.PLAYER,
                publication_doi="10.1234/Michael-Jordan-teams",
                dataset_doi="10.1234/Michael-Jordan-teams",
                tags="nba, jordan, teams",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=10,
                title="Pau Gasol Teams",
                description="Dataset about Pau-Gasol-teams",
                publication_type=PublicationType.PLAYER,
                publication_doi="10.1234/Pau-Gasol-teams",
                dataset_doi="10.1234/Pau-Gasol-teams",
                tags="nba, gasol, teams",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=11,
                title="Playoffs 2004-05",
                description="Dataset about playoffs-2004-05",
                publication_type=PublicationType.PLAYOFFS,
                publication_doi="10.1234/playoffs-2004-05",
                dataset_doi="10.1234/playoffs-2004-05",
                tags="nba, playoffs, 2004",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=12,
                title="Season 2023-24",
                description="Dataset about season-2023-24",
                publication_type=PublicationType.SEASON,
                publication_doi="10.1234/season-2023-24",
                dataset_doi="10.1234/season-2023-24",
                tags="nba, season, 2023",
                ds_metrics_id=seeded_ds_metrics.id,
            ),
            DSMetaData(
                deposition_id=13,
                title="Spurs Ring Winners",
                description="Dataset about spurs-ring-winners",
                publication_type=PublicationType.OTHER,
                publication_doi="10.1234/spurs-ring-winners",
                dataset_doi="10.1234/spurs-ring-winners",
                tags="nba, spurs, rings",
                ds_metrics_id=seeded_ds_metrics.id,
                extra_fields="Blocks per game, Steals per game",
            )
        ]
        seeded_ds_meta_data = self.seed(nba_datasets)

        nba_authors = [
            # Dataset: East Regular Season Champs (Ahora es el Índice 0)
            Author(
                name="NBA History Dept",
                affiliation="NBA League Office",
                orcid="0000-0002-1823-1111",
                ds_meta_data_id=seeded_ds_meta_data[0].id,
            ),
            # Dataset: Marc Gasol Teams (Índice 1)
            Author(
                name="Grizzlies Analytics",
                affiliation="Memphis Grizzlies",
                orcid="0000-0002-1823-2222",
                ds_meta_data_id=seeded_ds_meta_data[1].id,
            ),
            # Dataset: Pau Gasol Playoffs Teams (Índice 2)
            Author(
                name="Lakers Data Science",
                affiliation="LA Lakers",
                orcid="0000-0002-1823-3333",
                ds_meta_data_id=seeded_ds_meta_data[2].id,
            ),
            # Dataset: Playoffs 1996-97 (Índice 3)
            Author(
                name="Michael Jordan Archive",
                affiliation="Chicago Bulls Museum",
                orcid="0000-0002-1823-4444",
                ds_meta_data_id=seeded_ds_meta_data[3].id,
            ),
            # Dataset: Playoffs Conference Champs (Índice 4)
            Author(
                name="Sports Reference",
                affiliation="Basketball Reference",
                orcid="0000-0002-1823-5555",
                ds_meta_data_id=seeded_ds_meta_data[4].id,
            ),
            # Dataset: Season 2024-25 (Índice 5)
            Author(
                name="Current Season Tracker",
                affiliation="ESPN Stats & Info",
                orcid="0000-0002-1823-6666",
                ds_meta_data_id=seeded_ds_meta_data[5].id,
            ),
            # Dataset: West Regular Season Champs (Índice 6)
            Author(
                name="Western Conf Reporter",
                affiliation="The Athletic",
                orcid="0000-0002-1823-7777",
                ds_meta_data_id=seeded_ds_meta_data[6].id,
            ),
            # Dataset: Marc Gasol Playoffs Teams (Índice 7)
            Author(
                name="Marc Gasol Fan Club",
                affiliation="Spanish Basketball Federation",
                orcid="0000-0002-1823-8888",
                ds_meta_data_id=seeded_ds_meta_data[7].id,
            ),
            # Dataset: Michael Jordan Teams (Índice 8)
            Author(
                name="Phil Jackson",
                affiliation="Chicago Bulls",
                orcid="0000-0002-1823-9999",
                ds_meta_data_id=seeded_ds_meta_data[8].id,
            ),
            # Dataset: Pau Gasol Teams (Índice 9)
            Author(
                name="FC Barcelona Basket",
                affiliation="Euroleague Stats",
                orcid="0000-0002-1823-1010",
                ds_meta_data_id=seeded_ds_meta_data[9].id,
            ),
            # Dataset: Playoffs 2004-05 (Índice 10)
            Author(
                name="Detroit Pistons Legacy",
                affiliation="Motor City Archives",
                orcid="0000-0002-1823-1212",
                ds_meta_data_id=seeded_ds_meta_data[10].id,
            ),
            # Dataset: Season 2023-24 (Índice 11)
            Author(
                name="Recap 2023",
                affiliation="NBA Official Stats",
                orcid="0000-0002-1823-1313",
                ds_meta_data_id=seeded_ds_meta_data[11].id,
            ),
            # Dataset: Spurs Ring Winners (Índice 12)
            Author(
                name="Gregg Popovich",
                affiliation="San Antonio Spurs",
                orcid="0000-0002-1823-1414",
                ds_meta_data_id=seeded_ds_meta_data[12].id,
            ),
        ]
        self.seed(nba_authors)

        datasets = [
            DataSet(
                user_id=user1.id if i % 2 == 0 else user2.id,
                ds_meta_data_id=meta_data.id,
                created_at=datetime.now(timezone.utc),
            )
            for i, meta_data in enumerate(seeded_ds_meta_data)
        ]
        seeded_datasets = self.seed(datasets)

        load_dotenv()
        working_dir = os.getenv("WORKING_DIR", "")
        src_folder_csv = os.path.join(working_dir, "app", "modules", "dataset", "csv_examples")

        nba_dataset_names = [
            "east-regular-season-champs", "Marc-Gasol-teams", "Pau-Gasol-playoffs-teams",
            "playoffs-1996-97", "playoffs-conference-champs", "season-2024-25",
            "west-regular-season-champs", "Marc-Gasol-playoffs-teams", "Michael-Jordan-teams",
            "Pau-Gasol-teams", "playoffs-2004-05", "season-2023-24", "spurs-ring-winners"
        ]

        for i, folder_name in enumerate(nba_dataset_names):
            dataset = seeded_datasets[i]
            user_id = dataset.user_id
            dataset_folder_path = os.path.join(src_folder_csv, folder_name)
            if os.path.isdir(dataset_folder_path):
                csv_files = [f for f in os.listdir(dataset_folder_path) if f.endswith('.csv')]

                print(f"Procesando carpeta '{folder_name}': encontrados {len(csv_files)} archivos.")

                for csv_filename in csv_files:
                    fm_meta = FMMetaData(
                        csv_filename=csv_filename,
                        title=csv_filename.replace(".csv", "").replace("_", " ").title(),
                        description=f"Data file {csv_filename} belonging to {folder_name}",
                        publication_type=PublicationType.PLAYER,
                        publication_doi=f"10.1234/{csv_filename}",
                        tags="nba, csv, team-data",
                        uvl_version=None
                    )
                    seeded_fm_meta = self.seed([fm_meta])[0]

                    file_author = Author(
                        name="NBA Stats Registry",
                        affiliation="NBA Data Lake",
                        orcid="0000-0000-0000-0000",
                        fm_meta_data_id=seeded_fm_meta.id
                    )
                    self.seed([file_author])

                    feature_model = FeatureModel(
                        data_set_id=dataset.id,
                        fm_meta_data_id=seeded_fm_meta.id
                    )
                    seeded_feature_model = self.seed([feature_model])[0]
                    src_file_path = os.path.join(dataset_folder_path, csv_filename)
                    dest_folder = os.path.join(working_dir, "uploads", f"user_{user_id}", f"dataset_{dataset.id}")
                    os.makedirs(dest_folder, exist_ok=True)

                    shutil.copy(src_file_path, dest_folder)

                    dest_file_path = os.path.join(dest_folder, csv_filename)
                    hub_file = Hubfile(
                        name=csv_filename,
                        checksum=f"checksum_{csv_filename}",
                        size=os.path.getsize(dest_file_path),
                        feature_model_id=seeded_feature_model.id
                    )
                    self.seed([hub_file])

            else:
                print(f"ADVERTENCIA: No se encontró la carpeta: {dataset_folder_path}")
