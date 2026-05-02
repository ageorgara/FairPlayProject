import CONSTANTS
from CONSTANTS import FEATURES, PRICING_POLICIES
from random import shuffle
from Reservation import Reservation

class Hotel:
    def __init__(self,id,rooms,details = None, pricing_policy=PRICING_POLICIES.FAIRPLAY):
        self.id = id
        self.rooms = rooms
        for r in self.rooms:
            r.setHotelId(self.id)
        self.__pp = pricing_policy
        self.details = details
        self.__exposure_counter = 0

    def getAvailableRooms(self, day, room_type = None):
        if room_type:
            return [r for r in self.rooms if r.isfree(day) and r.getFeature(FEATURES.TYPE)==room_type]
        return [r for r in self.rooms if r.isfree(day)]

    def getBookedRooms(self, day, room_type = None):
        if room_type:
            return [r for r in self.rooms if r.isbooked(day) and r.getFeature(FEATURES.TYPE)==room_type]
        return [r for r in self.rooms if r.isbooked(day)]

    def getNumberOfRooms(self, room_type = None):
        if room_type:
            return len([r for r in self.rooms if r.getFeature(FEATURES.TYPE)==room_type])
        return len(self.rooms)

    def getNumberOfAvailableRooms(self, day, room_type = None):
        if room_type:
            return len([r for r in self.rooms if r.isfree(day) and r.getFeature(FEATURES.TYPE)==room_type])
        return len([r for r in self.rooms if r.isfree(day)])

    def getNumberOfReservedRooms(self, day, room_type = None):
        if room_type:
            return len([r for r in self.rooms if r.isbooked(day) and r.getFeature(FEATURES.TYPE)==room_type])
        return len([r for r in self.rooms if r.isbooked(day)])

    def bookRoom(self, day, roomId = None, roomType = None, increment=0):
        if roomId:
            for r in self.rooms:
                if r.id == roomId:
                    price = r.getValue() * (1+increment)
                    reservation = Reservation(hotel_id=self.id,room=r,day=day,price=price)
                    # r.book(day)
                    return reservation
            print(f'Could not find room with room id {roomId}')
            return

        if roomType:
            for r in self.rooms:
                if r.isfree(day) and r.getFeature(FEATURES.TYPE) == roomType:
                    # print(f'\t\t\t(Booking room with id {r.id})')
                    price = r.getValue() * (1+increment)
                    reservation = Reservation(hotel_id=self.id,room=r,day=day,price=price)
                    # r.book(day)
                    return reservation

            print(f'Could not find avaialbe room of room type {roomType}')
            return

        shuffle(self.rooms)
        for r in self.rooms:
            if r.isfree(day):
                r.book(day)
                return
        print(f'Could not find available room.')
        return

    # def cancelRoom(self, day, roomId=None):
    #     if roomId:
    #         for r in self.rooms:
    #             if r.id == roomId:
    #                 r.cancel(day)
    #                 return
    #     for r in self.rooms:
    #         if r.isbooked(day):
    #             r.cancel(day)
    #             return r.getValue()

    def findRoom(self,roomID=None,room_type=None,day=None):
        if roomID:
            for r in self.rooms:
                if r.id==roomID:
                    return r
            print(f"Could not find room {roomID}.")
            return None
        elif room_type:
            for r in self.rooms:
                if r.getFeature(FEATURES.TYPE)==room_type and r.isfree(day):
                    return r
            print(f"Could not find room of type {room_type}")
            return None
        else:
            print("Room id or room type is required!")
            return None
    def setPricingPolicy(self,policy):
        self.__pp = policy
        for r in self.rooms:
            r.setPricingPolicy(policy)
    def getPricingPolicy(self):
        return self.__pp

    def exposed(self):
        self.__exposure_counter+=1
    def getExposureCounter(self):
        return self.__exposure_counter

    # def __eq__(self, other):
    #     # return isinstance(other, Hotel) and self.id == other.id
    #     return isinstance(other, Hotel) and self.__name.lower() == other.getName().lower()
    #
    # def __lt__(self, other):
    #     # return isinstance(other, Hotel) and self.id < other.id
    #     return isinstance(other, Hotel) and self.__name.lower() < other.getName().lower
    #
    # def __gt__(self, other):
    #     # return isinstance(other, Hotel) and self.id > other.id
    #     return isinstance(other, Hotel) and self.__name.lower() > other.getName().lower
    #
    # def __le__(self, other):
    #     # return isinstance(other, Hotel) and self.id <= other.id
    #     return isinstance(other, Hotel) and self.__name.lower() <= other.getName().lower
    #
    # def __ge__(self, other):
    #     # return isinstance(other, Hotel) and self.id >= other.id
    #     return isinstance(other, Hotel) and self.__name.lower() >= other.getName().lower

    def __str__(self):
        return str(self.id)

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return str(self.id)  # f'''Hotel {self.id} in {self.__location} with {self.__total_power_in_rooms} rooms'''
    @staticmethod
    def loadHotelsCSV(file,time_period=None):
        import pandas as pd
        df = pd.read_csv(file)
        return Hotel.decodeHotelFromDataframe(df, time_period)

    @staticmethod
    def decodeHotelFromDataframe(df,time_period):
        from Room import Room
        hotels = []
        hotels_ids = df["Hotel id"].unique().tolist()
        for index, row in df.iterrows():
            hotel_id = row["Hotel id"]
            if hotel_id in hotels_ids:
                policy = row["Pricing Policy"]
                rooms = Room.decodeRoomsFromDataframe(df[df["Hotel id"]==hotel_id],time_period)
                new_hotel = Hotel(id = str(hotel_id), rooms = rooms)
                new_hotel.setPricingPolicy(policy)
                hotels.append(new_hotel)
                hotels_ids.remove(hotel_id)
        return hotels

    @staticmethod
    def freeAll(hotels_list):
        for h in hotels_list:
            for r in h.rooms:
                r.free()
    @staticmethod
    def findHotel(hotels_list,hotel_id):
        for h in hotels_list:
            if h.id == hotel_id:
                return h
        print(f"Hotel with id {hotel_id} was not found!")
        return

if __name__ == '__main__':
    from random import choice
    file = "Datasets/70Fairplay30+50%.csv"
    hotels = Hotel.loadHotelsCSV(file,time_period=30)
    for h in hotels:
        p = choice(CONSTANTS.PRICING_POLICIES.DEFAULT_POLICIES)
        print(h.id,p)