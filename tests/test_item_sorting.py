import unittest
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from models.item import Item
from routes.items import apply_item_sorting, apply_item_filters


class ItemSortingTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(bind=self.engine)

    def test_sort_by_newest_first(self):
        self.session.add_all([
            Item(title="Alpha", description="first", created_at=datetime(2024, 1, 1, 8, 0, 0)),
            Item(title="Bravo", description="second", created_at=datetime(2024, 1, 3, 8, 0, 0)),
            Item(title="Charlie", description="third", created_at=datetime(2024, 1, 2, 8, 0, 0)),
        ])
        self.session.commit()

        ordered = apply_item_sorting(self.session.query(Item), "newest").all()
        self.assertEqual([item.title for item in ordered], ["Bravo", "Charlie", "Alpha"])

    def test_sort_by_title_asc(self):
        self.session.add_all([
            Item(title="Charlie", description="third", created_at=datetime(2024, 1, 1, 8, 0, 0)),
            Item(title="Alpha", description="first", created_at=datetime(2024, 1, 2, 8, 0, 0)),
            Item(title="Bravo", description="second", created_at=datetime(2024, 1, 3, 8, 0, 0)),
        ])
        self.session.commit()

        ordered = apply_item_sorting(self.session.query(Item), "title_asc").all()
        self.assertEqual([item.title for item in ordered], ["Alpha", "Bravo", "Charlie"])

    def test_filter_matches_title_or_description(self):
        self.session.add_all([
            Item(title="Alpha Project", description="Need review", created_at=datetime(2024, 1, 1, 8, 0, 0)),
            Item(title="Beta", description="Marketing notes", created_at=datetime(2024, 1, 2, 8, 0, 0)),
            Item(title="Gamma", description="Support checklist", created_at=datetime(2024, 1, 3, 8, 0, 0)),
        ])
        self.session.commit()

        filtered = apply_item_filters(self.session.query(Item), "project").all()
        self.assertEqual([item.title for item in filtered], ["Alpha Project"])

        filtered = apply_item_filters(self.session.query(Item), "notes").all()
        self.assertEqual([item.title for item in filtered], ["Beta"])


if __name__ == "__main__":
    unittest.main()
