from random import randint

from instapy import InstaPy, smart_run

ACCOUNTS_PATH = 'accounts.txt'

session = InstaPy(
    headless_browser=False
)

def iter_all_followers(session, accounts):
    followers = set()
    for account in accounts:
        followers.update(session.grab_followers(username=account, amount='full'))
    for follower in followers:
        yield follower

def do_actions_with_user(session, username):
    # Enable and watch stories
    session.set_do_story(enabled=True, percentage=100, simulate=True)
    session.story_by_users([username])
    session.set_do_story(enabled=False)
    # Five a likes
    session.interact_by_users([username], amount=randint(1, 5))

def iter_get_all_accounts():
    with open(ACCOUNTS_PATH, 'r') as file:
        for line in file.readlines():
            yield line.strip()

    

with smart_run(session):
    # settings
    # Skip private
    session.set_skip_users(skip_private=True, private_percentage=100)
    # Eanble liking
    session.set_do_like(True, percentage=100)

    for follower in iter_all_followers(session, iter_get_all_accounts()):
        do_actions_with_user(session, follower)