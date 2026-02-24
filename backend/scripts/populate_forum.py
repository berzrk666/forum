# Run with:
# `uv run scripts/populate_forum.py`

import logging
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from forum.auth.models import User, hash_password, Role
from forum.category.models import Category
from forum.config import settings
from forum.forum.models import Forum
from forum.post.models import Post  # noqa
from forum.thread.models import Thread

log = logging.getLogger(__name__)

engine = create_engine(str(settings.DATABASE_URI))

# Roles
role_admin = Role(name="admin")
role_mod = Role(name="moderator")
role_user = Role(name="user")

# Users
admin = User(
    username="admin",
    password=hash_password("admin"),
    email="admin@example.com",
    role=role_admin,
)

mod = User(
    username="moderator",
    password=hash_password("moderator"),
    email="moderator@example.com",
    role=role_mod,
)

user = User(
    username="user",
    password=hash_password("user"),
    email="user@example.com",
    role=role_user,
)

user2 = User(
    username="user2",
    password=hash_password("user2"),
    email="user2@example.com",
    role=role_user,
)

user3 = User(
    username="user3",
    password=hash_password("user3"),
    email="user3@example.com",
    role=role_user,
)
user4 = User(
    username="user4",
    password=hash_password("user4"),
    email="user4@example.com",
    role=role_user,
)
user5 = User(
    username="user5",
    password=hash_password("user5"),
    email="user5@example.com",
    role=role_user,
)


# Categories
general = Category(name="General", order=1)
technology = Category(name="Technology", order=2)
offtopic = Category(name="Off-Topic", order=3)


# Forums
announcements = Forum(
    name="Announcements",
    description="Official announcements and news",
    order=1,
    category=general,
)

introductions = Forum(
    name="Introductions",
    description="New here? Say hello!",
    order=2,
    category=general,
)

programming = Forum(
    name="Programming",
    description="Discuss programing languages, frameworks, and tools",
    order=3,
    category=technology,
)


hardware = Forum(
    name="Hardware",
    description="CPUs, GPUs, builds and peripherals",
    order=4,
    category=technology,
)

networking = Forum(
    name="Networking",
    description="Routers, switches, protocols and home labs",
    order=5,
    category=technology,
)

lounge = Forum(
    name="Lounge",
    description="Chat about anything and everything",
    order=6,
    category=offtopic,
)

gaming = Forum(
    name="Gaming",
    description="Video games, board games, and more",
    order=7,
    category=offtopic,
)

# Threads
t1 = Thread(
    title="Hi everyone!",
    author=user3,
    forum=introductions,
    content="Hello everyone, I am user3",
)
t2 = Thread(
    title="Hello",
    author=user2,
    forum=introductions,
    content="Hello",
)
t3 = Thread(title="Ademir", author=admin, forum=introductions, content="I am ademir")
t4 = Thread(title="Yo", author=mod, forum=introductions, content="Yoooooooo ;)")
t5 = Thread(title="o/", author=user5, forum=introductions, content="o/ o/ \\o/")

t6 = Thread(
    title="Forum Rules - Read First",
    author=admin,
    is_pinned=True,
    is_locked=True,
    forum=announcements,
    content="There is no rules.",
)

t7 = Thread(
    title="Looking for people to play Elden Ring Coop",
    author=user5,
    forum=gaming,
    content="add me on steam",
)
t8 = Thread(
    title="Anyone wanna play any game??",
    author=user3,
    forum=gaming,
    content="any games, any platforms, any skills",
)

t9 = Thread(
    title="Whats the difference between switches and hubs ?",
    author=user2,
    forum=networking,
    content="What are their differences ? Or they are just the same ?",
)
t10 = Thread(
    title="RTX 4070ti or RX 7900 XT",
    author=user2,
    forum=hardware,
    content="Which one is the best in 2026? Will both run minecraft smoothly ?",
)

t11 = Thread(
    title="Cyberpunk benchmark",
    author=user,
    forum=hardware,
    content="Benchmark comparions in cyberpunk with a GTX 690, i3-3990k",
)

t12 = Thread(
    title="Python or Go in 2026",
    author=user3,
    forum=programming,
    content="Which on should I prioritize this year ? I am no beginner programmer, but I am looking to learn something new; )",
)
t13 = Thread(
    title="Python Resources",
    author=admin,
    forum=programming,
    is_pinned=True,
    content="Here are some good books for python: Python Book 1, Python Book 2, Python Book 3, ...",
)

t14 = Thread(
    title="Which country to travel in 2026?",
    author=user5,
    forum=lounge,
    content="Looking for some places to travel this year. What are your recommendations ?",
)


def create_users():
    """Create sample users."""
    with Session(engine) as session:
        session.add_all([admin, mod, user, user2, user3, user4, user5])
        session.commit()


def create_categories():
    """Create basic categories"""
    with Session(engine) as session:
        session.add_all([general, technology, offtopic])
        session.commit()


def create_forums():
    """Create basic forums."""
    with Session(engine) as session:
        session.add_all(
            [
                announcements,
                introductions,
                programming,
                hardware,
                networking,
                lounge,
                gaming,
            ]
        )
        session.commit()


def create_threads():
    with Session(engine) as session:
        session.add_all([t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14])
        session.commit()


if __name__ == "__main__":
    log.info("Creating users")
    create_users()
    log.info("Users created successfully")
    log.info("Creating categories")
    create_categories()
    log.info("Categories created successfully")
    log.info("Creating forums")
    create_forums()
    log.info("Forums created successfully")
    log.info("Creating threads")
    create_threads()
    log.info("Threads created successfully")
