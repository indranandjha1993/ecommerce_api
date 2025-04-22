import uuid
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.category import Category
from app.repositories.base import BaseRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryRepository(BaseRepository[Category, CategoryCreate, CategoryUpdate]):
    """
    Category repository for data access operations.
    """

    def get_by_slug(self, db: Session, slug: str) -> Optional[Category]:
        """
        Get a category by slug.
        """
        return db.query(Category).filter(Category.slug == slug).first()

    def get_with_children(self, db: Session, id: uuid.UUID) -> Optional[Category]:
        """
        Get a category with its children.
        """
        # Get the category first
        category = db.query(Category).filter(Category.id == id).first()
        
        if category:
            # Manually get children
            children = db.query(Category).filter(Category.parent_id == id).all()
            setattr(category, 'children', children)
            
        return category

    def get_by_slug_with_children(self, db: Session, slug: str) -> Optional[Category]:
        """
        Get a category by slug with its children.
        """
        # Get the category first
        category = db.query(Category).filter(Category.slug == slug).first()
        
        if category:
            # Manually get children
            children = db.query(Category).filter(Category.parent_id == category.id).all()
            setattr(category, 'children', children)
            
        return category

    def get_root_categories(self, db: Session) -> List[Category]:
        """
        Get all root categories (with no parent).
        """
        return (
            db.query(Category)
            .filter(Category.parent_id.is_(None))
            .order_by(Category.display_order.asc(), Category.name.asc())
            .all()
        )

    def get_category_tree(self, db: Session) -> List[Category]:
        """
        Get the complete category tree.
        """
        # Get all root categories
        root_categories = (
            db.query(Category)
            .filter(Category.parent_id.is_(None))
            .order_by(Category.display_order.asc(), Category.name.asc())
            .all()
        )
        
        # For each root category, get its children
        for category in root_categories:
            children = db.query(Category).filter(Category.parent_id == category.id).all()
            setattr(category, 'children', children)
            
            # For each child, get its children (grandchildren of root)
            for child in children:
                grandchildren = db.query(Category).filter(Category.parent_id == child.id).all()
                setattr(child, 'children', grandchildren)
        
        return root_categories

    def create_with_slug_check(self, db: Session, obj_in: CategoryCreate) -> Category:
        """
        Create a category with slug uniqueness check.
        """
        # Check if a category with this slug already exists
        existing_category = self.get_by_slug(db, slug=obj_in.slug)
        if existing_category:
            raise ValueError(f"A category with slug '{obj_in.slug}' already exists")

        # Create category
        return self.create(db, obj_in=obj_in)

    def update_with_slug_check(
            self, db: Session, *, db_obj: Category, obj_in: CategoryUpdate
    ) -> Category:
        """
        Update a category with slug uniqueness check.
        """
        # Check if slug is being changed and if it's already in use
        if obj_in.slug and obj_in.slug != db_obj.slug:
            existing_category = self.get_by_slug(db, slug=obj_in.slug)
            if existing_category and existing_category.id != db_obj.id:
                raise ValueError(f"A category with slug '{obj_in.slug}' already exists")

        # Update category
        return self.update(db, db_obj=db_obj, obj_in=obj_in)


category_repository = CategoryRepository(Category)
