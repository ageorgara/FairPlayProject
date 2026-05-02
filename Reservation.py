from Room import Room

class Reservation:
    def __init__(self, hotel_id, room:Room,day:int, price:float):
        self.hotel_id = hotel_id
        self.room = room
        self.day = day
        self.price = price
        self.book()

    def book(self):
        self.room.book(self.day)

    def cancel(self):
        self.room.cancel(self.day)
