from CONSTANTS import TIME_PERIOD, FEATURES, PRICING_POLICIES
class Room:
    def __init__(self,id, MEP, features = None, time_period=None, pricing_policy = PRICING_POLICIES.FAIRPLAY, hotel_id = None):
        self.id =id
        self.__value = MEP
        self.__pp = pricing_policy
        self.__initialize(time_period, features)
        self.__hotel_id = hotel_id

    def __initialize(self,time_period, features):
        if time_period is None or time_period<=0:
            time_period = TIME_PERIOD.ONE_MONTH
        self.period = time_period
        self.__available = [True for i in range(time_period)]
        if features is None:
            features = {f:FEATURES.DEFAULT_VALUE[f] for f in FEATURES.DEFAULT_LIST_OF_FEATURES}
        self.features = features


    def setHotelId(self,hid):
        self.__hotel_id = hid
    def getHotelId(self):
        return self.__hotel_id
    def getValue(self):
        return self.__value
    def setValue(self,newMEP):
        self.__value = newMEP
    def isfree(self, day):
        try:
            return self.__available[day]
        except:
            print(f"Day {day} is beyond the scope of this time period ({self.period} days)")

    def isbooked (self,day):
        try:
            return not self.__available[day]
        except:
            print(f"Day {day} is beyond the scope of this time period ({self.period} days)")

    def book(self, day):
        try:
            self.__available[day] = False
            return True
        except:
            print(f"Day {day} is beyond the scope of this time period ({self.period} days)")

    def cancel(self,day):
        try:
            self.__available[day] = True
            return True
        except:
            print(f"Day {day} is beyond the scope of this time period ({self.period} days)")

    def free(self):
        self.__available = [True for i in range(self.period)]
    def getFeature(self,feature):
        if feature in self.features:
            return self.features[feature]
        print(f"Feature {feature} is not within room's features")
        return None

    def sameFeature(self,other,feature):
        return isinstance(other, Room) and (feature in self.features and feature in other.features) and (self.features[feature] == other.features[feature])

    def __eq__(self, other):
        return isinstance(other, Room) and self.id == other.id

    def __lt__(self, other):
        return isinstance(other, Room) and self.id < other.id

    def __gt__(self, other):
        return isinstance(other, Room) and self.id > other.id

    def __le__(self, other):
        return isinstance(other, Room) and self.id <= other.id

    def __ge__(self, other):
        return isinstance(other, Room) and self.id >= other.id

    def __str__(self):
        return str(self.id)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return f'''{self.id}'''
    def setPricingPolicy(self,policy):
        self.__pp = policy
    def getPricingPolicy(self):
        return self.__pp

    ''' 
    TO DO:
        Loaders and Decoders from file
    '''
    @staticmethod
    def loadRoomsCSV(file,time_period=None):
        import pandas as pd
        df = pd.read_csv(file)
        return Room.decodeRoomsFromDataframe(df,time_period)

    @staticmethod
    def decodeRoomsFromDataframe(df,time_period):
        if time_period is None:
            time_period = TIME_PERIOD.ONE_MONTH
        rooms = []
        for index,row in df.iterrows():
            room_id = row["Room id"]
            room_type = row["Room Type"].lower()
            MEP = float(row["Price"])
            room = Room(id=room_id,MEP=MEP,features={FEATURES.TYPE:room_type},time_period=time_period)
            rooms.append(room)
        return rooms