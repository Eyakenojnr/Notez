"""Main application module.
"""
from app import app, db
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import User, Note, Group, ToDoList, ToDoItem, Tag


@app.shell_context_processor
def make_shell_context():
    """Create shell context that adds the database instance and models to
    the shell session.
    """
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Note': Note,
            'Group': Group, 'ToDoList': ToDoList, 'ToDoItem': ToDoItem, 'Tag': Tag}
