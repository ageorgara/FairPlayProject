import pandas as pd
from random import choice, randint, sample, random

import CONSTANTS
from CONSTANTS import FEATURES
from math import ceil
import json
size={
        "large":100,
        "medium":50,
        "small":20,
        "tiny" : 10
    }

def generator(ss):
    number_of_hotels = size[ss]
    max_number_of_rooms_per_hotel = 30
    min_number_of_rooms_per_hotel = 20

    file = "Synthetic2 (also good) (good)"
    price_ranges = {"low cost": [30, 60], "med cost": [65, 100], "high cost": [130, 250]}
    df = pd.DataFrame(columns=["Hotel id", "City", "Room id", "Price", "Room Type", "Pricing Policy"])
    policy = {price_range: [] for price_range in price_ranges}

    total_number_of_rooms_created = 0
    for hidx in range(number_of_hotels):
        hotel_id = f"Hotel_00{hidx}" if hidx < 10 else f"Hotel_0{hidx}"
        price_range = choice(list(price_ranges.keys()))
        # price_range = "eq"
        policy[price_range].append(hotel_id)
        number_of_rooms = randint(min_number_of_rooms_per_hotel, max_number_of_rooms_per_hotel)
        room_types = {}
        rm_rooms = number_of_rooms
        print(hotel_id, price_range)
        for room_type in FEATURES.OPTIONS[FEATURES.TYPE]["LIST_OF_OPTIONS"]:
            if rm_rooms == 0:
                continue
            nr = randint(0, rm_rooms)
            price = randint(price_ranges[price_range][0], price_ranges[price_range][1])
            room_types[room_type] = [nr, price]
            rm_rooms -= nr
        if rm_rooms > 0:
            room_type = choice(list(room_types.keys()))
            room_types[room_type][0] += rm_rooms
        cnt = 0
        for room_type in room_types:
            for i in range(room_types[room_type][0]):
                # Create a room to append in the df
                new_room = {}
                new_room["Hotel id"] = hotel_id
                new_room["City"] = "Atlantis"
                new_room["Room id"] = f"{hotel_id}_Room_00{cnt}" if cnt < 10 else f"{hotel_id}_Room_0{cnt}"
                new_room["Price"] = room_types[room_type][1]
                new_room["Room Type"] = room_type
                total_number_of_rooms_created += 1
                df = df._append(new_room, ignore_index=True)
                cnt += 1

    # c = choice(policy["eq"])
    # fairplay_ids = [ i for i in policy["eq"] if i!=c]
    policies_ids = {p: [] for p in ["fairplay", "+40%", "+50%", "+60%"]}
    for price_range in price_ranges:
        for hid in policy[price_range]:
            hotels_policy = choice(["fairplay", "+40%", "+50%", "+60%"])
            policies_ids[hotels_policy].append(hid)
            df.loc[df["Hotel id"] == hid, "Pricing Policy"] = hotels_policy

    df.to_csv(f"{file}.csv", index=False)

    with open(f"{file}_FairPlay_policy.json", "w") as f:
        json.dump(policies_ids, f, indent=4)
    print(f"Created:\n\t{number_of_hotels} hotels\n\t{total_number_of_rooms_created} rooms")

def identical(ss,pp,filename):
    number_of_hotels = int(size[ss]/len(pp))
    max_number_of_rooms_per_hotel = 20
    min_number_of_rooms_per_hotel = 10

    price_ranges = {"low cost": [30, 60], "med cost": [65, 100], "high cost": [130, 250]}
    df = pd.DataFrame(columns=["Hotel id", "City", "Room id", "Price", "Room Type", "Pricing Policy"])
    # policy = {price_range: [] for price_range in price_ranges}
    price_range = "low cost" #choice(list(price_ranges.keys()))

    number_of_rooms = randint(min_number_of_rooms_per_hotel, max_number_of_rooms_per_hotel)
    room_types = {}
    rm_rooms = number_of_rooms
    for room_type in FEATURES.OPTIONS[FEATURES.TYPE]["LIST_OF_OPTIONS"]:
        if rm_rooms == 0:
            continue
        nr = randint(0, rm_rooms)
        price = randint(price_ranges[price_range][0], price_ranges[price_range][1])
        room_types[room_type] = [nr, price]
        rm_rooms -= nr
    if rm_rooms > 0:
        room_type = choice(list(room_types.keys()))
        room_types[room_type][0] += rm_rooms

    p = 0
    for policy in pp:
        for hidx in range(p,p+number_of_hotels):
            cnt = 0
            hotel_id = f"Hotel_00{hidx}" if hidx < 10 else f"Hotel_0{hidx}"
            for room_type in room_types:
                for i in range(room_types[room_type][0]):
                    new_room = {}
                    new_room["Hotel id"] = hotel_id
                    new_room["City"] = "Atlantis"
                    new_room["Room id"] = f"{hotel_id}_Room_00{cnt}" if cnt < 10 else f"{hotel_id}_Room_0{cnt}"
                    new_room["Price"] = room_types[room_type][1]
                    new_room["Room Type"] = room_type
                    new_room["Pricing Policy"] = policy
                    df = df._append(new_room, ignore_index=True)
                    cnt += 1
        p+=number_of_hotels

    df.sort_values(["Hotel id"])
    df.to_csv(filename, index=False)

def manyIdenticalEq(ss,pp,filename):
    number_of_hotels = int(size[ss] / len(pp))
    max_number_of_rooms_per_hotel = 30
    min_number_of_rooms_per_hotel = 20

    price_ranges = {"low cost": [30, 60], "med cost": [65, 100], "high cost": [130, 250]}
    df = pd.DataFrame(columns=["Hotel id", "City", "Room id", "Price", "Room Type", "Pricing Policy"])

    for i in range(0,2*number_of_hotels,2):
        price_range = choice(list(price_ranges.keys()))
        number_of_rooms = randint(min_number_of_rooms_per_hotel, max_number_of_rooms_per_hotel)
        room_types = {}
        rm_rooms = number_of_rooms

        for room_type in FEATURES.OPTIONS[FEATURES.TYPE]["LIST_OF_OPTIONS"]:
            if rm_rooms == 0:
                continue
            nr = randint(0, rm_rooms)
            price = randint(price_ranges[price_range][0], price_ranges[price_range][1])
            room_types[room_type] = [nr, price]
            rm_rooms -= nr
        if rm_rooms > 0:
            room_type = choice(list(room_types.keys()))
            room_types[room_type][0] += rm_rooms
        cnt = 0

        hidx = i
        for policy in pp:
            hotel_id = f"Hotel_00{hidx}" if hidx < 10 else f"Hotel_0{hidx}"
            for room_type in room_types:
                for i in range(room_types[room_type][0]):
                    # Create a room to append in the df
                    new_room = {}
                    new_room["Hotel id"] = hotel_id
                    new_room["City"] = "Atlantis"
                    new_room["Room id"] = f"{hotel_id}_Room_00{cnt}" if cnt < 10 else f"{hotel_id}_Room_0{cnt}"
                    new_room["Price"] = room_types[room_type][1]
                    new_room["Room Type"] = room_type
                    new_room["Pricing Policy"] = policy
                    df = df._append(new_room, ignore_index=True)
                    cnt += 1
            hidx+=1
    df.sort_values(["Hotel id"])
    df.to_csv(filename, index=False)

def manyIdentical(ss,pp,filename,n):
    nohs = {
        p: int(size[ss]*n[p]) for p in n
    }
    print(nohs)
    max_number_of_rooms_per_hotel = 30
    min_number_of_rooms_per_hotel = 20

    price_ranges = {"low cost": [30, 60], "med cost": [65, 100], "high cost": [130, 250]}
    df = pd.DataFrame(columns=["Hotel id", "City", "Room id", "Price", "Room Type", "Pricing Policy"])

    hotel_data =[]

    price_range = "low cost" #choice(list(price_ranges.keys()))
    number_of_rooms = randint(min_number_of_rooms_per_hotel, max_number_of_rooms_per_hotel)
    room_types = {}
    rm_rooms = number_of_rooms
    for room_type in ["double"]: #FEATURES.OPTIONS[FEATURES.TYPE]["LIST_OF_OPTIONS"]:
        if rm_rooms == 0:
            continue
        nr = randint(0, rm_rooms)
        price = randint(price_ranges[price_range][0], price_ranges[price_range][1])
        room_types[room_type] = [nr, price]
        rm_rooms -= nr
    if rm_rooms > 0:
        room_type = choice(list(room_types.keys()))
        room_types[room_type][0] += rm_rooms
    for room_type in room_types:
        for i in range(room_types[room_type][0]):
            # Create a room to append in the df
            new_room = {}
            new_room["City"] = "Atlantis"
            new_room["Price"] = room_types[room_type][1]
            new_room["Room Type"] = room_type
            hotel_data.append(new_room)
    hidx = 0
    cnt = 0
    for policy in pp:
        for i in range(nohs[policy]):
            hotel_id = f"Hotel_00{hidx}" if hidx < 10 else f"Hotel_0{hidx}"
            for new_room in hotel_data:
                new_room["Hotel id"] = hotel_id
                new_room["Room id"] = f"{hotel_id}_Room_00{cnt}" if cnt < 10 else f"{hotel_id}_Room_0{cnt}"
                new_room["Pricing Policy"] = policy
                df = df._append(new_room, ignore_index=True)
                cnt += 1
            hidx+=1
    df.sort_values(["Hotel id"])
    df.to_csv(filename, index=False)


def manyNonIdentical(ss,pp,filename,n):
    nohs = {
        p: int(size[ss]*n[p]) for p in n
    }
    print(nohs)
    max_number_of_rooms_per_hotel = 25
    min_number_of_rooms_per_hotel = 20

    price_ranges = {"low cost": [30, 60], "med cost": [65, 100], "high cost": [130, 250]}
    # price_ranges = {
    #     CONSTANTS.PRICING_POLICIES.FAIRPLAY: [30, 50],
    #     CONSTANTS.PRICING_POLICIES.SEVENTEEN_PRC:[40,60],
    #     CONSTANTS.PRICING_POLICIES.FORTY_PRC:[40,60],
    #     CONSTANTS.PRICING_POLICIES.FIFTY_PRC:[40,60]
    # }
    df = pd.DataFrame(columns=["Hotel id", "City", "Room id", "Price", "Room Type", "Pricing Policy"])
    hidx = 0
    for policy in pp:
        for i in range(nohs[policy]):
            hotel_id = f"Hotel_00{hidx}" if hidx < 10 else f"Hotel_0{hidx}"

            price_range = choice(list(price_ranges.keys()))
            # price_range = policy
            number_of_rooms = randint(min_number_of_rooms_per_hotel, max_number_of_rooms_per_hotel)
            room_types = {}
            rm_rooms = number_of_rooms
            for room_type in FEATURES.OPTIONS[FEATURES.TYPE]["LIST_OF_OPTIONS"]:
                if rm_rooms == 0:
                    continue
                nr = randint(0, rm_rooms)
                price = randint(price_ranges[price_range][0], price_ranges[price_range][1])
                room_types[room_type] = [nr, price]
                rm_rooms -= nr
            if rm_rooms > 0:
                room_type = choice(list(room_types.keys()))
                room_types[room_type][0] += rm_rooms
            cnt = 0
            for room_type in room_types:
                for i in range(room_types[room_type][0]):
                    # Create a room to append in the df
                    new_room = {}
                    new_room["Hotel id"] = hotel_id
                    new_room["City"] = "Atlantis"
                    new_room["Room id"] = f"{hotel_id}_Room_00{cnt}" if cnt < 10 else f"{hotel_id}_Room_0{cnt}"
                    new_room["Price"] = room_types[room_type][1]
                    new_room["Room Type"] = room_type
                    new_room["Pricing Policy"] = policy
                    df = df._append(new_room, ignore_index=True)
                    cnt += 1
            hidx+=1
    df.sort_values(["Hotel id"])
    df.to_csv(filename, index=False)


if __name__ == '__main__':
    ss = "small"
    pp = [
        CONSTANTS.PRICING_POLICIES.FAIRPLAY,
        CONSTANTS.PRICING_POLICIES.SEVENTEEN_PRC,
        # CONSTANTS.PRICING_POLICIES.TWENTY_PRC,
        CONSTANTS.PRICING_POLICIES.FORTY_PRC,
        CONSTANTS.PRICING_POLICIES.FIFTY_PRC,
        # CONSTANTS.PRICING_POLICIES.SIXTY_PRC
    ]
    # generator(ss)
    fp = 25
    cn = 25
    cn2 = 25
    cn3 = 25

    for cnt in range(1,11):
        filename = f"Identical_FP_vs_+17%_vs_+40%_vs_+50% ({ss} {fp} vs {cn} vs {cn2} vs {cn3})_{cnt}.csv"
        manyIdentical(ss=ss, pp=pp, filename=filename,
                         n={
                            CONSTANTS.PRICING_POLICIES.FAIRPLAY:fp/100,
                            CONSTANTS.PRICING_POLICIES.SEVENTEEN_PRC: cn/100,
                            CONSTANTS.PRICING_POLICIES.FORTY_PRC: cn2/100,
                            CONSTANTS.PRICING_POLICIES.FIFTY_PRC: cn3/100,
                         })
        # filename = f"Non_Identical_FP_vs_+17%_vs_+40%_vs_+50% ({ss}3 {fp} vs {cn} vs {cn2} vs {cn3}).csv"
        manyNonIdentical(ss=ss, pp=pp, filename="Non_"+filename,
                         n={
                            CONSTANTS.PRICING_POLICIES.FAIRPLAY:fp/100,
                            CONSTANTS.PRICING_POLICIES.SEVENTEEN_PRC: cn/100,
                            CONSTANTS.PRICING_POLICIES.FORTY_PRC: cn2/100,
                            CONSTANTS.PRICING_POLICIES.FIFTY_PRC: cn3/100,
                         })


