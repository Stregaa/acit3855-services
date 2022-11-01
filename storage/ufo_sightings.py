from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base
import datetime

class UFOSighting(Base):
    """ UFO Sighting """

    __tablename__ = "ufo_sightings"

    id = Column(Integer, primary_key=True)
    description = Column(String(250), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    number = Column(Integer, nullable=False)
    shape = Column(String(250), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    date_created = Column(DateTime, nullable=False)  
    trace_id = Column(Integer, nullable=False)  

    def __init__(self, description, latitude, longitude, number, shape, timestamp, trace_id):
        """ Initializes a UFO sighting """
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
        self.number = number
        self.shape = shape
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a UFO sighting """
        dict = {}
        dict['id'] = self.id
        dict['description'] = self.description
        dict['latitude'] = self.latitude
        dict['longitude'] = self.longitude
        dict['number'] = self.number
        dict['shape'] = self.shape
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
