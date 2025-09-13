"""Database models for the Notez application.
"""
from typing import List, Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import enum


class GenderEnum(enum.Enum):
    """Enum class.
    """

    male = 'male'
    female = 'female'
    other = 'other'

# --- Association Tables for Many-to-Many Relationships ---
note_tag_association = sa.Table(
    'note_tag',
    db.metadata,
    sa.Column('note_id', sa.ForeignKey('note.id'), primary_key=True),
    sa.Column('tag_id', sa.ForeignKey('tag.id'), primary_key=True)
)

todolist_tag_association = sa.Table(
    'todolist_tag',
    db.metadata,
    sa.Column('todolist_id', sa.ForeignKey('to_do_list.id'), primary_key=True),
    sa.Column('tag_id', sa.ForeignKey('tag.id'), primary_key=True)
)


# --- Main Model Classes ---
class User(UserMixin, db.Model):
    """User database model.

    Args:
        UserMixin (class): Class that includes safe implementations of flask_login 
            requirements for user model classes.
        db (class): Base class.
    """

    __tablename__ = 'user'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    first_name: so.Mapped[str] = so.mapped_column(sa.String(80))
    last_name: so.Mapped[str] = so.mapped_column(sa.String(80))
    gender: so.Mapped[GenderEnum] = so.mapped_column(
        sa.Enum(GenderEnum, name='gender_enum', native_enum=False),
        nullable=True
    )
    username: so.Mapped[str] = so.mapped_column(sa.String(80), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256))
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    
    # Relationships
    notes: so.Mapped[List["Note"]] = so.relationship(
        back_populates="author", cascade="all, delete-orphan")
    groups: so.Mapped[List["Group"]] = so.relationship(
        back_populates="author", cascade="all, delete-orphan")
    tags: so.Mapped[List["Tag"]] = so.relationship(
        back_populates="creator", cascade="all, delete-orphan")
    todolists: so.Mapped[List["ToDoList"]] = so.relationship(
        back_populates="author", cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size=128):
        """Generates a gender-specific avatar using the DiceBear API.
        Uses a neutral style if gender is not specified.
        """
        # Use username as unique seed for the avatar
        seed = self.username.lower()

        style = "adventurer"

        if self.gender in [GenderEnum.male, GenderEnum.female]:
            gender_option = f"&gender={self.gender.value}"
            return f"https://api.dicebear.com/8.x/{style}/svg?seed={seed}{gender_option}&size={size}"
        else:
            initials = (self.first_name[0] + self.last_name[0]).upper()
            return f"https://api.dicebear.com/8.x/initials/svg?seed={initials}&size={size}&background-color=00897b,00acc1,26a69a"

    

class Note(db.Model):
    """Notes database model.
    """

    __tablename__ = 'note'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(200), nullable=True)
    content: so.Mapped[str] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    deleted_at: so.Mapped[datetime | None] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True)
    
    # Foreign Keys
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), index=True)
    group_id: so.Mapped[int | None] = so.mapped_column(sa.ForeignKey('group.id'), nullable=True)

    # ORM relationships
    author: so.Mapped["User"] = so.relationship(back_populates="notes")
    category: so.Mapped[Optional["Group"]] = so.relationship(back_populates="notes")
    tags: so.Mapped[List["Tag"]] = so.relationship(
        secondary=note_tag_association, back_populates="notes")

    def __repr__(self):
        return f'<Note {self.title}>'
    

class Group(db.Model):
    """Group database model.
    """

    __tablename__ = 'group'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(200))
    description: so.Mapped[str | None] = so.mapped_column(sa.Text, nullable=True)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    deleted_at: so.Mapped[datetime | None] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True)
    
    # Foreign Keys
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), index=True)

    # ORM relationships
    author: so.Mapped["User"] = so.relationship(back_populates="groups") # User who owns this group
    notes: so.Mapped[List["Note"]] = so.relationship(back_populates="category")
    todolists: so.Mapped[List["ToDoList"]] = so.relationship(back_populates="category")

    def __repr__(self):
        return f"<Group {self.name}>"
    

class ToDoList(db.Model):
    """Todo list database model.
    """

    __tablename__ = 'to_do_list'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(200))
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    deleted_at: so.Mapped[datetime | None] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True)
    
    # Foreign Keys
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'))
    group_id: so.Mapped[int | None] = so.mapped_column(
        sa.ForeignKey('group.id'), nullable=True)
    
    # ORM Relationships
    author: so.Mapped["User"] = so.relationship(back_populates="todolists")
    category: so.Mapped[Optional["Group"]] = so.relationship(back_populates="todolists")
    items: so.Mapped[List["ToDoItem"]] = so.relationship(
        back_populates="todolist", cascade="all, delete-orphan")
    tags: so.Mapped[List["Tag"]] = so.relationship(
        secondary=todolist_tag_association, back_populates="todolists")
    
    def __repr__(self):
        return f"<ToDoList {self.title}>"
    

class ToDoItem(db.Model):
    """Todo list items database model."""

    __tablename__ = 'to_do_item'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    description: so.Mapped[str] = so.mapped_column(sa.String(500))
    is_completed: so.Mapped[bool] = so.mapped_column(
        sa.Boolean, default=False, server_default=sa.false())
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: so.Mapped[datetime | None] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True)
    due_date: so.Mapped[datetime | None] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True)
    reminder_time: so.Mapped[datetime | None] = so.mapped_column(
        sa.DateTime(timezone=True), nullable=True)
    
    # Foreign Key
    todolist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('to_do_list.id'), index=True)

    # ORM Relationships
    todolist: so.Mapped["ToDoList"] = so.relationship(back_populates="items")

    def __repr__(self):
        return f'<ToDoItem {self.description[:30]}>'
    

class Tag(db.Model):
    """Tags database model."""

    __tablename__ = 'tag'
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), unique=True, index=True)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    # A tag can be global (user_id is NULL) or user-specific.
    user_id: so.Mapped[int | None] = so.mapped_column(sa.ForeignKey('user.id'), nullable=True)

    # ORM Relationships
    creator: so.Mapped[Optional["User"]] = so.relationship(back_populates="tags")
    notes: so.Mapped[List["Note"]] = so.relationship(
        secondary=note_tag_association, back_populates="tags")
    todolists: so.Mapped[List["ToDoList"]] = so.relationship(
        secondary=todolist_tag_association, back_populates="tags")
    
    def __repr__(self):
        return f'<Tag {self.name}>'
    

@login.user_loader
def load_user(id):
    """User loader function.

    Args:
        id (string): ID of user to be loaded.

    Returns:
        object: Returns a User object or None.
    """
    return db.session.get(User, int(id))
