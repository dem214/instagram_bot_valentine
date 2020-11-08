#! /usr/bin/python
from random import randint, sample
import os
import time
import logging
from datetime import datetime, timedelta
import pathlib

from instapy import InstaPy, smart_run
from sqlalchemy import create_engine, Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
import yaml

DATABASE_NAME = 'accounts.sqlite3'
EXPIRATION_DATE_OF_FAMOUS_ACCOUNT = timedelta(days=7)
AMMOUNT_OF_ACCOUNTS = 260

# Database
engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Session = sessionmaker()
Session.configure(bind=engine)
orm_session = Session()
Base = declarative_base()

with open('config.yml', 'r') as f:
    CONFIG = yaml.full_load(f)


class FamousAccount(Base):
    __tablename__ = 'famous_account'

    username = Column(String, primary_key=True)
    date_of_adding = Column(DateTime)

    def __str__(self):
        return f"Famous account '{self.username}"

    @staticmethod
    def iter_get_usernames_from_source():
        for username in CONFIG['accounts']:
            yield username

    @staticmethod
    def create_with_dbing(username):
        try:
            famous = orm_session.query(FamousAccount).\
                filter(FamousAccount.username == username).one()
            print(famous)
        except NoResultFound:
            session.logger.info(f"adding new famous account {username}")
            famous = FamousAccount(
                username=username,
                date_of_adding=datetime.now() - 2 * EXPIRATION_DATE_OF_FAMOUS_ACCOUNT)
            orm_session.add(famous)
            print(famous)
        finally:
            return famous

    def is_expired(self):
        """
        check if famous account is not expired.
        """
        session.logger.info(f"Try to check expiration of {self.username} -- {self.date_of_adding}")
        session.logger.info(f"time for last connectiong is {datetime.now() - self.date_of_adding}")
        return datetime.now() - self.date_of_adding > \
            EXPIRATION_DATE_OF_FAMOUS_ACCOUNT


class Account(Base):
    __tablename__ = 'accounts'
  
    username = Column(String, primary_key=True)
    is_checked = Column(Boolean)

    REST_TIME_AFTER_ITERACT_MIN = 35
    REST_TIME_AFTER_ITERACT_MAX = 55

    def __str__(self):
        return f"Account '{self.username}'"

    def iteract(self, session):
        session.logger.info(f"Interacting with {self.username}!")
        self._method_of_interraction(session)
        self.is_checked = True
        orm_session.commit()

    def _method_of_interraction(self, session):
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
                session.logger.info(f"Adding new account {username}")
                orm_session.add(Account(username=username, is_checked=False))
        famous.date_of_adding = datetime.now()
        orm_session.commit()
        session.logger.info(f"Famous account {famous.username} date of upload updated to {famous.date_of_adding}")

    @staticmethod
    def get_random_unchecked_accounts_from_db(amount):
        all_unchecked = orm_session.query(Account).\
            filter(Account.is_checked==False).\
            all()
        try:
            resp = sample(all_unchecked, amount)
        except ValueError:
            session.logger.info('Not enough accounts in db')
            if len(all_unchecked) == 0:
                resp = None
            else:
                resp = sample(all_unchecked, len(all_unchecked))
        return resp

    def _rest_after_iteract(self):
        rest_time = randint(
            self.REST_TIME_AFTER_ITERACT_MIN, 
            self.REST_TIME_AFTER_ITERACT_MAX)
        session.logger.info(f"i'm little tyred, sleep {rest_time} seconds")
        time.sleep(rest_time)
        print("i'd rested, lets go")

   
if __name__ == '__main__':
    # Check db or create
    if not os.path.exists(DATABASE_NAME):
        print("create db")
        Base.metadata.create_all(engine)

    # Logging
    log_dir = pathlib.Path('.') / 'logs'
    # Creat log dir
    if not log_dir.exists():
        os.mkdir(log_dir)
    fhandler = logging.FileHandler(
        log_dir / '{:%Y-%m-%d}.log'.format(datetime.now())
    )
    lformatter = logging.Formatter(
        '%(levelname)s [%(asctime)s] [%(name)s] - %(message)s'
    )
    fhandler.setFormatter(lformatter)

    session = InstaPy(
        headless_browser=False,
        log_handler=fhandler
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
            peak_likes_hourly=CONFIG['likes_hourly'],
            peak_likes_daily=CONFIG['likes_daily']
        )

        usernames = FamousAccount.iter_get_usernames_from_source()
        famouses = map(FamousAccount.create_with_dbing, usernames)
        expired_famouses = (famous for famous in famouses if famous.is_expired())
        for famous in expired_famouses:
            Account.saving_follovers_of_famous(session, famous)
        session.logger.info("Start to iteract with amount")
        while accounts := Account.get_random_unchecked_accounts_from_db(
                AMMOUNT_OF_ACCOUNTS):
            for account in accounts:
                account.iteract(session)
            session.logger.info("Ended with amount")
        session.logger.info("Ended with all accounts in db")
