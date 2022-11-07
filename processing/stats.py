from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class Stats(Base):
    """ Processing Statistics """

    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)
    num_ufo_sightings = Column(Integer, nullable=False)
    curr_ufo_num = Column(Integer, nullable=True)
    num_cryptid_sightings = Column(Integer, nullable=False)
    curr_cryptid_num = Column(Integer, nullable=True)
    last_updated = Column(DateTime, nullable=False)

    def __init__(self, num_ufo_sightings, curr_ufo_num, num_cryptid_sightings, curr_cryptid_num, last_updated):
        """ Initializes a processing statistics object """
        self.num_ufo_sightings = num_ufo_sightings
        self.curr_ufo_num = curr_ufo_num
        self.num_cryptid_sightings = num_cryptid_sightings
        self.curr_cryptid_num = curr_cryptid_num
        self.last_updated = last_updated

    def to_dict(self):
        """ Dictionary Representation of statistics """
        dict = {}
        dict['id'] = self.id
        dict['num_ufo_sightings'] = self.num_ufo_sightings
        dict['curr_ufo_num'] = self.curr_ufo_num
        dict['num_cryptid_sightings'] = self.num_cryptid_sightings
        dict['curr_cryptid_num'] = self.curr_cryptid_num
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")

        return dict
