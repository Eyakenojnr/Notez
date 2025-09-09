"""Seeding script.
"""
import random
from faker import Faker
from app import app, db
from app.models import User, Note, Group, ToDoList, ToDoItem, Tag
from datetime import datetime, timedelta, timezone


fake = Faker()

def run_seed(num_users=50):
    """Seeds the database with specific amount of realistic fake data.

    Args:
        num_users (int, optional): Number of users to create. Defaults to 50.
    """
    print("Dropping and recreating database tables...")
    db.drop_all()
    db.create_all()

    print("Preparing seed data in memory...")

    # Create all objects in memory first
    users, groups, all_notes, all_todolists, all_todo_items, all_tags = [], [], [], [], [], []
    groups_by_user = {}

    # Create Users
    print(f"Creating {num_users} users...")
    for _ in range(num_users):
        users.append(User(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            password_hash='fake_password_hash',  # Remember to hash this properly in real app
            created_at=fake.date_time_between(start_date="-2y", end_date="now", tzinfo=timezone.utc)
        ))

    # Create Groups and assign it to users
    print("Creating user groups...")
    for user in users:
        # Each user gets 1 to 4 groups
        user_groups = []
        for _ in range(random.randint(1, 4)):
            group = Group(
                name=fake.word().capitalize() + " Folder",
                description=fake.sentence(),
                author=user
            )
            groups.append(group)
            user_groups.append(group)
        groups_by_user[user.username] = user_groups  # Using a unique key (i.e. username) before IDs exist

    # Create Notes and ToDoLists
    print("Creating notes and to-do lists...")
    for user in users:
        # None included as a possibilty for items that don't belong to a group
        user_group_choices = groups_by_user.get(user.username, []) + [None]

        # Create 10 to 100 Notes per user
        for _ in range(random.randint(10, 100)):
            all_notes.append(Note(
                title=fake.sentence(nb_words=6),
                content=fake.paragraph(nb_sentences=10),
                author=user,
                category=random.choice(user_group_choices)
            ))

        # Create 3 to 15 ToDoLists per user
        for _ in range(random.randint(3, 15)):
            # Manually set created_at to be used for ToDoItems later
            list_created_at = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=timezone.utc)

            all_todolists.append(ToDoList(
                title=f"{fake.word().capitalize()} Project",
                author=user,
                category=random.choice(user_group_choices),
                created_at=list_created_at
            ))

    # Create ToDoItems
    print("Creating to-do items...")
    for todolist in all_todolists:
        # Each list gets 3 to 20 items
        for _ in range(random.randint(3, 20)):
            is_completed = fake.boolean(chance_of_getting_true=40)
            completed_at = None
            if is_completed:
                # Set completed_at to a time after the list was created
                completed_at = todolist.created_at + timedelta(days=random.randint(1, 60))

            # Set due date b/w 1 to 30 days in the future
            due_date = datetime.now(timezone.utc) + timedelta(days=random.randint(1, 30))

            item = ToDoItem(
                description=fake.sentence(nb_words=10),
                is_completed=is_completed,
                todolist=todolist,
                completed_at=completed_at,
                due_date=due_date
            )
            all_todo_items.append(item)

    # Create Tags
    print("Creating tags...")
    for i in range(50): # 50 unique tags
        # 30% chance the tag is global (no creator)
        creator = random.choice(users) if random.random() < 0.7 else None

        tag = Tag(
            name=fake.unique.word().lower(),
            creator=creator
        )
        all_tags.append(tag)

    # Add all created objects to the session
    db.session.add_all(users)
    db.session.add_all(groups)
    db.session.add_all(all_notes)
    db.session.add_all(all_todolists)
    db.session.add_all(all_todo_items)
    db.session.add_all(all_tags)

    # Create Many-to-Many Associations for Tags
    print("Creating tag associations...")

    # Tag Notes
    for note in all_notes:
        # Assign 0 to 3 random tags
        note.tags = random.sample(all_tags, random.randint(0, 3))

    # Tag ToDoLists
    for todolist in all_todolists:
        # Assign 0 to 2 random tags
        todolist.tags = random.sample(all_tags, random.randint(0, 2))

    print("Committing the transaction...")
    db.session.commit()

    print("\n--- Seeding Completed ---")
    print(f"Users: {num_users}")
    print(f"Groups: {len(groups)}")
    print(f"Notes: {len(all_notes)}")
    print(f"To-Do Lists: {len(all_todolists)}")
    print(f"To-Do Items: {len(all_todo_items)}")
    print(f"Tags: {len(all_tags)}")


if __name__ == '__main__':
    with app.app_context():
        run_seed()
