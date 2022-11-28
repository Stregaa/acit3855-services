from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class Health(Base):
    """ Health Statistics """

    __tablename__ = "health"

    id = Column(Integer, primary_key=True)
    receiver = Column(String(20), nullable=False)
    storage = Column(String(20), nullable=False)
    processing = Column(String(20), nullable=False)
    audit = Column(String(20), nullable=False)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, receiver, storage, processing, audit, last_updated):
        """ Initializes a health check object """
        self.receiver = receiver
        self.curr_ufo_num = storage
        self.num_cryptid_sightings = processing
        self.curr_cryptid_num = audit
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of statistics """
        dict = {}
        dict['id'] = self.id
        dict['receiver'] = self.receiver
        dict['storage'] = self.storage
        dict['processing'] = self.processing
        dict['audit'] = self.audit
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")

        return dict
