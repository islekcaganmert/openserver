from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, UTC

Base = declarative_base()


class Mail(Base):
    __tablename__ = 'mails'
    id = Column(Integer, primary_key=True)
    mailbox = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    sender = Column(String)
    to = Column(String)  # ;
    cc = Column(String)  # ;
    hashtag = Column(String)
    body = Column(String)
    encrypted = Column(Boolean, default=False)
    date_received = Column(DateTime, default=datetime.now(UTC))

    def json(self):
        return {
            "subject": self.subject,
            "date_received": self.date_received.strftime('%Y-%m-%d %H:%M'),
            "sender": self.sender,
            "to": self.to.split(';'),
            "cc": self.cc.split(';'),
            "hashtag": self.hashtag,
            "body": self.body,
            'from': self.sender
        }


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    chat = Column(String)
    sender = Column(String)
    body = Column(String)
    encrypted = Column(Boolean, default=False)
    date_received = Column(DateTime, default=datetime.now(UTC))

    def json(self):
        return {
            "from": self.sender,
            "body": self.body,
            "date_received": self.date_received.strftime('%Y-%m-%d %H:%M')
        }


class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    handler = Column(String)
    image = Column(String)
    title = Column(String)
    participants = Column(String)  # ;

    def json(self):
        return {
            "image": self.image,
            "title": self.title,
            "participants": self.participants.split(';')
        }  # add last_index: int before sending


class DB:
    def __init__(self, username: str = None, create_now: bool = False):
        if username is not None:
            self.__engine = create_engine(f'sqlite:///Users/{username}/Library/Mails.db')
            if create_now:
                Base.metadata.create_all(self.__engine)
            self.__session = sessionmaker(bind=self.__engine)()

    def list_mailboxes(self):
        r = {'Archive': 0, 'Primary': 0, 'Promotions': 0, 'Sent': 0, 'Social': 0, 'Spam': 0, 'Trash': 0}
        for mail in self.__session.query(Mail).order_by(Mail.id):
            if mail.mailbox not in r:
                r.update({mail.mailbox: 1})
            else:
                r[mail.mailbox] += 1
        return r

    def add_mail(self, subject, sender, to, cc, hashtag, body, encrypted, mailbox='Primary'):
        new_mail = Mail(
            mailbox=mailbox,
            subject=subject,
            sender=sender,
            to=';'.join(to),
            cc=';'.join(cc),
            hashtag=hashtag,
            body=body,
            encrypted=encrypted
        )
        self.__session.add(new_mail)
        self.__session.commit()

    def get_mail(self, mailbox, id):
        return self.__session.query(Mail).filter_by(mailbox=mailbox).all()[int(id) - 1].json()

    def move_mail(self, mailbox, id, move_to):
        mail = self.__session.query(Mail).filter_by(mailbox=mailbox).all()[int(id) - 1]
        if move_to == '-':
            self.__session.delete(mail)
        else:
            mail.mailbox = move_to
        self.__session.commit()

    def list_chats(self):
        r = {chat.handler: chat.json() for chat in self.__session.query(Chat).order_by(Chat.title).all()}
        for message in self.__session.query(Message).order_by(Message.id).all():
            if message.chat not in r:
                r.update({message.chat: {}})
        for chat in r:
            r[chat.handler].update({
                'last_index': len(self.__session.query(Message).order_by(Message.id).filter_by(chat=chat.id).all())
            })
        return r

    def add_message(self, sender, body, chat, encrypted):
        new_message = Message(
            chat=chat,
            sender=sender,
            body=body,
            encrypted=encrypted
        )
        self.__session.add(new_message)
        self.__session.commit()

    def add_chat(self, handler, image, title, participants):
        new_chat = Chat(
            handler=handler,
            image=image,
            title=title,
            participants=';'.join(participants)
        )
        self.__session.add(new_chat)
        self.__session.commit()

    def get_chat(self, id):
        return self.__session.query(Chat).filter_by(id=id).all()[0].json()

    def get_message(self, chat, id):
        return self.__session.query(Message).filter_by(chat=chat).all()[int(id) - 1].json()
