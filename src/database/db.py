import sqlite3
import logging
import database.db_config  as config
import Action 


class dataBase():
     
     def __init__(self):
          try:     
               self.logger = logging.getLogger(__name__)
               self.connection = sqlite3.connect(config.DB_PATH)
               self.cursor = self.connection.cursor()
               if self.connection is not None:
                     self.connection.execute(config.TABLE_ACTIONS)
                     self.connection.execute(config.TABLE_ACTIONS_EPCS)
          
          except sqlite3.Error as err:
               self.logger.error(f"Database creation exception:", err.args)





     def save(self,action):
          try:
               self.cursor.execute('INSERT INTO actions(deviceType,deviceId,locationId,checkTime,checkDuration,actionTime,light,volume,reason) VALUES (?,?,?,?,?,?,?,?)', 
                       (action.deviceType, action.deviceId, action.locationId,action.checkTime,action.checkDuration,self.actionTime,
                        action.light,action.volume,action.reason))
               self.connection.commit()
               self.cursor.close()
               self.connection.close()
          except Exception as ex:
               self.logger.error(f"Error executiong query: ",ex.args)


     def getAll(self):
          try:
               _all = []
               self.cursor.execute('SELECT * FROM actions')
               result = self.cursor.fetchall()
               
               for i in result:
                    row = list(i)
                    _all.append(Action(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
               
               self.cursor.close()
               self.connection.close()
               return _all      

          except Exception as ex:
               self.logger.error(f"Error executiong query: ",ex.args)
               return None     
          


     def delete(self, action):
          try:

               self.QRY_DELETE = """DELETE FROM actions WHERE id = ?"""
               self.cursor.execute(self.QRY_DELETE , (action.id,))
               return True
          
          except Exception as ex:
               self.logger.error(f"Error executiong query: ",ex.args)
               return None     
          
    