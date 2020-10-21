from random import randint

from instapy import InstaPy, smart_run

ACCOUNTS_PATH = 'accounts.txt'

session = InstaPy(
    headless_browser=False
)

def iter_all_followers(session, accounts, amount="full"):
    followers = set()
    for account in accounts:
        followers.update(session.grab_followers(username=account, amount=amount))
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
    session.set_skip_users(skip_private=True, private_percentage=80)
    # Eanble liking
    session.set_do_like(True, percentage=70)
    # Enable story watching
    session.set_do_story(enabled=True, percentage=90)
    # Quota supervising
    session.set_quota_supervisor(
        enabled=True,
        sleep_after=['likes_h', 'likes_d'],
        sleepyhead=True,
        stochastic_flow=True,
        peak_likes_hourly=58,
        peak_likes_daily=1405
    )

    followers = iter_all_followers(session, iter_get_all_accounts(), amount=260)
    session.interact_by_users(list(followers), randomize=True, amount=5)
