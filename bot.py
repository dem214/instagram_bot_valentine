#! /usr/bin/python
from random import randint, sample
import os
import time

from instapy import InstaPy, smart_run
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

ACCOUNTS_PATH = 'accounts.txt'
DATABASE_NAME = 'accounts.sqlite3'
AMMOUNT_OF_ACCOUNTS = 260

engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Session = sessionmaker()
Session.configure(bind=engine)
orm_session = Session()

Base = declarative_base()

def iter_all_followers(session, accounts, amount="full"):
    followers = set()
    for account in accounts:
        followers.update(session.grab_followers(username=account, amount=amount))
    for follower in followers:
        yield Account(follower)


class FamousAccount(Base):
    __tablename__ = 'famous_account'

    username = Column(String, primary_key=True)

    @staticmethod
    def iter_from_file_with_dbing(file=ACCOUNTS_PATH):
        with open(file, 'r') as file:
            for line in file.readlines():
                username = line.strip()
                try:
                    famous = orm_session.query(FamousAccount).\
                        filter(FamousAccount.username == username).one()
                except NoResultFound:
                    print(f"adding new famous account {username}")
                    famous = FamousAccount(username=username)
                    orm_session.add(famous)
                yield famous

class Account(Base):
    __tablename__ = 'accounts'
    
    username = Column(String, primary_key=True)
    is_checked = Column(Boolean)
    REST_TIME_AFTER_ITERACT_MIN = 35
    REST_TIME_AFTER_ITERACT_MAX = 55

    def iteract(self, session):
        print(f"Iteracting with {self.username}!")
        self._method_of_iterraction(session)
        self.is_checked = True
        orm_session.commit()

    def _method_of_iterraction(self, session):        
        session.interact_by_users(self.username, amount=randint(1, 5))
        self._rest_after_iteract()


    @staticmethod
    def saving_follovers_of_famous(session, famous, amount='full'):
        for username in session.grab_followers(username=famous.username, amount=amount):
            try:
                account = orm_session.query(Account).\
                    filter(Account.username == username).\
                    one()
            except NoResultFound:
                print(f"Adding new account {username}")
                orm_session.add(Account(username=username, is_checked=False))

    @staticmethod
    def get_random_unchecked_accounts_from_db(amount):
        all_unchecked = orm_session.query(Account).\
            filter(Account.is_checked == False).\
            all()
        try:
            resp = sample(all_unchecked, amount)
        except ValueError:
            print('Not enough accounts in db')
            if len(all_unchecked) == 0:
                resp = None
            else:
                resp = sample(all_unchecked, len(all_unchecked))
        return resp

    def _rest_after_iteract(self):
        rest_time = randint(self.REST_TIME_AFTER_ITERACT_MIN, self.REST_TIME_AFTER_ITERACT_MAX)
        print("i'm little tyred, sleep {rest_time} seconds")
        time.sleep(rest_time)
        print("i'd rested, lets go")

    
if __name__ == '__main__':
    # Check db or create
    if not os.path.exists(DATABASE_NAME):
        print("create db")
        Base.metadata.create_all(engine)

    session = InstaPy(
        headless_browser=False
    )
    with smart_run(session):
        # settings
        # Skip private
        session.set_skip_users(skip_private=True, private_percentage=80)
        # Eanble liking
        session.set_do_like(True, percentage=90)
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

        print('saving accounts from famous')
        for famous in FamousAccount.iter_from_file_with_dbing():
            Account.saving_follovers_of_famous(session, famous)
        print("start to iteract with amount")
        while accounts := Account.get_random_unchecked_accounts_from_db(AMMOUNT_OF_ACCOUNTS):
            for account in accounts:
                account.iteract(session)
            print("ended with amount")
        print("ended with all accounts in db")
