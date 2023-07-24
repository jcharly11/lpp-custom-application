from dbm import _Database
import sqlite3

from database.db_config import db_config


class actions_model(object):

    def __init__(self, deviceType='', deviceId='', locationId='', checkTime=0, checkDuration=0, actionTime=0,
                 light='', volume=0, reason=''):
        self.deviceType = deviceType
        self.deviceId = deviceId
        self.locationId = locationId
        self.checkTime = checkTime
        self.checkDuration= checkDuration
        self.actionTime= actionTime
        self.light= light
        self.volume= volume
        self.reason= reason

    def save_action(self):
        connection= db_config.connect_db
        cursor = connection.cursor()
        cursor.execute('INSERT INTO actions(deviceType,deviceId,locationId,checkTime,checkDuration,actionTime,light,volume,reason) VALUES (?,?,?,?,?,?,?,?)', 
                       (self.deviceType, self.deviceId, self.locationId,self.checkTime,self.checkDuration,self.actionTime,
                        self.light,self.volume,self.reason))        
        connection.commit()
        cursor.close()
        db_config.disconnect_db(connection)
        
        
    @staticmethod
    def get_actions():
        _all = []
        connection= db_config.connect_db
        cursor = connection.cursor()
    
        cursor.execute('SELECT * FROM actions')
        result = cursor.fetchall()
        
        for i in result:
            row = list(i)
            _all.append(actions_model(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
        
        cursor.close()
        db_config.disconnect_db(connection)
        
        return _all        
    