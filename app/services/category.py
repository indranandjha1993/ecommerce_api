import uuid
from typing import List

from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.models.category import Category
from app.repositories.category import category_repository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryTreeItem


class CategoryService:
    """
    Category service for business logic.
    """

    def get_by_id(self, db: Session, category_id: uuid.UUID) -> Category:
        """
        Get a category by ID.
        """
        category = category_repository.get(db, id=category_id)
        if not category:
            raise NotFoundException(detail="Category not found")
        return category

    def get_by_slug(self, db: Session, slug: str) -> Category:
        """
        Get a category by slug.
        """
        category = category_repository.get_by_slug(db, slug=slug)
        if not category:
            raise NotFoundException(detail="Category not found")
        return category

    def get_with_children(self, db: Session, category_id: uuid.UUID) -> Category:
        """
        Get a category with its children.
        """
        category = category_repository.get_with_children(db, id=category_id)
        if not category:
            raise NotFoundException(detail="Category not found")
        return category

    def get_by_slug_with_children(self, db: Session, slug: str) -> Category:
        """
        Get a category by slug with its children.
        """
        category = category_repository.get_by_slug_with_children(db, slug=slug)
        if not category:
            raise NotFoundException(detail="Category not found")
        return category

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
        """
        Get all categories with pagination.
        """
        return category_repository.get_multi(db, skip=skip, limit=limit)

    def get_root_categories(self, db: Session) -> List[Category]:
        """
        Get all root categories (with no parent).
        """
        return category_repository.get_root_categories(db)

    def get_category_tree(self, db: Session) -> List[CategoryTreeItem]:
        """
        Get the complete category tree.
        """
        categories = category_repository.get_category_tree(db)
        return self._build_category_tree(categories)

    def create(self, db: Session, category_in: CategoryCreate) -> Category:
        """
        Create a new category.
        """
        try:
            # If parent_id is provided, check if parent exists
            if category_in.parent_id:
                parent = category_repository.get(db, id=category_in.parent_id)
                if not parent:
                    raise NotFoundException(detail="Parent category not found")

            return category_repository.create_with_slug_check(db, obj_in=category_in)
        except ValueError as e:
            raise BadRequestException(detail=str(e))

    def update(self, db: Session, category_id: uuid.UUID, category_in: CategoryUpdate) -> Category:
        """
        Update a category.
        """
        category = category_repository.get(db, id=category_id)
        if not category:
            raise NotFoundException(detail="Category not found")

        try:
            # If parent_id is provided, check if parent exists and prevent circular reference
            if category_in.parent_id:
                if category_in.parent_id == category_id:
                    raise BadRequestException(detail="Category cannot be its own parent")

                parent = category_repository.get(db, id=category_in.parent_id)
                if not parent:
                    raise NotFoundException(detail="Parent category not found")

                # Check for circular reference in ancestry
                current_parent = parent
                while current_parent and current_parent.parent_id:
                    if current_parent.parent_id == category_id:
                        raise BadRequestException(detail="Circular reference detected in category hierarchy")
                    current_parent = category_repository.get(db, id=current_parent.parent_id)

            return category_repository.update_with_slug_check(db, db_obj=category, obj_in=category_in)
        except ValueError as e:
            raise BadRequestException(detail=str(e))

    def delete(self, db: Session, category_id: uuid.UUID) -> None:
        """
        Delete a category.
        """
        category = category_repository.get_with_children(db, id=category_id)
        if not category:
            raise NotFoundException(detail="Category not found")

        # Check if category has children
        if category.children:
            raise BadRequestException(detail="Cannot delete category with children")

        # Check if category has products
        if category.products:
            raise BadRequestException(detail="Cannot delete category with products")

        category_repository.remove(db, id=category_id)

    def _build_category_tree(self, categories: List[Category]) -> List[CategoryTreeItem]:
        """
        Build a tree structure from a list of categories.
        """
        result = []

        for category in categories:
            # Convert category to tree item
            tree_item = CategoryTreeItem(
                id=category.id,
                name=category.name,
                slug=category.slug,
                description=category.description,
                is_active=category.is_active,
                image_url=category.image_url,
                display_order=category.display_order,
                parent_id=category.parent_id,
                created_at=category.created_at,
                updated_at=category.updated_at,
                children=[]
            )

            # Add children recursively
            if hasattr(category, 'children') and category.children:
                tree_item.children = self._build_category_tree(category.children)

            result.append(tree_item)

        return result


category_service = CategoryService()
