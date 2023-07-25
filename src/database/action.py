class Action():
     
     def __init__(self,correlationId, epcs, deviceType, deviceId, locationId, checkTime, checkDuration, actionTime,
                 light, volume, reason):
        self.correlationId = correlationId,
        self.epcs =  epcs
        self.deviceType = deviceType
        self.deviceId = deviceId
        self.locationId = locationId
        self.checkTime = checkTime
        self.checkDuration= checkDuration
        self.actionTime= actionTime
        self.light= light
        self.volume= volume
        self.reason= reason