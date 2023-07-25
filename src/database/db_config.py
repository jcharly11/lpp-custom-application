DB_NAME = 'lpp-database.db'
DB_PATH = '../database/' + DB_NAME

TABLE_ACTIONS = """
    CREATE TABLE IF NOT EXISTS actions(
          [id] INTEGER PRIMARY KEY AUTOINCREMENT , 
          [correlationId] INT, 
          [deviceType] TEXT,
          [deviceId] TEXT,
          [checkTime] TIMESTAMP,
          [checkDuration] TIMESTAMP,
          [actionTime] TIMESTAMP,
          [light] TEXT,
          [volume] INT,
          [reason] TEXT
    );
    """

TABLE_ACTIONS_EPCS = """
    CREATE TABLE IF NOT EXISTS actions_epcs(
	      FOREIGN KEY (epc_id) REFERENCES actions (correlationId),
          [epc] TEXT
    );
    """
