import pandas as pd
import CONSTANTS
from OWEN import computeOwenValues as COV

def prepareIncomeSimulationDF(hotels, simulation_period):
    df = pd.DataFrame(
        columns=["Hotel Id", "Pricing Policy", "Init Day"] + ["Day " + str(d + 1) for d in
                                                                              range(simulation_period)]
    )
    df["Hotel Id"] = [str(h.id) for h in hotels]
    df["Pricing Policy"] = [str(h.getPricingPolicy()) for h in hotels]
    df["Init Day"] = [0 for i in range(len(hotels))]
    df.sort_values("Hotel Id")
    return df


def prepareOccupancySimulationDF(hotels, simulation_period):
    df = pd.DataFrame(
            columns=["Hotel Id", "Pricing Policy", "Total Number of Rooms", "Init Day"] + ["Day " + str(d + 1) for d in
                                                                                           range(simulation_period)]
        )
    df["Hotel Id"] = [str(h.id) for h in hotels]
    df["Pricing Policy"] = [str(h.getPricingPolicy()) for h in hotels]
    df["Total Number of Rooms"] = [float(h.getNumberOfRooms()) for h in hotels]
    df["Init Day"] = [0 for i in range(len(hotels))]
    df.sort_values("Hotel Id")
    return df

def preparePricesSimulationDF(hotels, simulation_period):
    df = pd.DataFrame(
        columns=["Hotel Id", "Room Id", "Pricing Policy", "Init Day"] + ["Day " + str(d + 1) for d in
                                                              range(simulation_period)]
    )
    df["Hotel Id"] = [str(h.id) for h in hotels for r in h.rooms]
    df["Room Id"] = [str(r.id) for h in hotels for r in h.rooms]
    df["Pricing Policy"] = [str(r.getPricingPolicy()) for h in hotels for r in h.rooms]
    incr = {r: 0 if r.getPricingPolicy() == CONSTANTS.PRICING_POLICIES.FAIRPLAY else CONSTANTS.PRICING_POLICIES.INCREMENT[r.getPricingPolicy()]
            for h in hotels for r in h.rooms
            }
    df["Init Day"] = [r.getValue()*(1+incr[r]) for h in hotels for r in h.rooms]
    df.sort_values("Hotel Id")
    return df
def fillinPriceDF(df, hotels, owen_values, day = "Init Day", init=False):
    if init:
        all_room_ids = [r.id for h in hotels for r in h.rooms]

        df["Room Type"] = [str(r.getFeature(CONSTANTS.FEATURES.TYPE)) for r in all_room_ids]
        df["Room Id"] = [str(r.id) for r in all_room_ids]
        df["Pricing Policy"] = [str(r.getPricingPolicy()) for r in all_room_ids]
        df["Hotel Id"] = [h.id for h in hotels for r in h.rooms]
    else:
        all_room_ids = df["Room Type"].tolist()
    column_values = []
    for r in all_room_ids:
        if r in owen_values:
            policy = r.getPricingPolicy()
            incr = owen_values[r] if policy == CONSTANTS.PRICING_POLICIES.FAIRPLAY else \
                CONSTANTS.PRICING_POLICIES.INCREMENT[policy]
            column_values.append(r.getValue() * (1 + incr))
        else:
            column_values.append("-")
    df[day] = column_values
    return df

def prepareIncomeSimulationAccumulateDF(simulation_period):
    df = pd.DataFrame(
        columns=["Iteration", "Pricing Policy", "Init Day"] + ["Day " + str(d + 1) for d in
                                                                         range(simulation_period)]
    )
    return df

def normalizePrice(x,y):
    return x/y

def preparePriceCompareDF(simulation_period, hotels, constant_incr):
    all_room_ids = [r for h in hotels for r in h.rooms]



    df_prices = pd.DataFrame(columns=["Room Type", "Room Id", "Hotel Id", "Init Day"] + ["Day " + str(d + 1) for d in
                                                                                         range(simulation_period)])
    df_prices_constant = pd.DataFrame(
        columns=["Room Type", "Room Id", "Hotel Id", "Init Day"] + ["Day " + str(d + 1) for d in
                                                                    range(simulation_period)])
    df_gain = pd.DataFrame(columns=["Room Type", "Room Id", "Hotel Id", "Init Day"] + ["Day " + str(d + 1) for d in
                                                                                       range(simulation_period)])
    df_gain_constant = pd.DataFrame(
        columns=["Room Type", "Room Id", "Hotel Id", "Init Day"] + ["Day " + str(d + 1) for d in
                                                                    range(simulation_period)])

    owen_values = COV(hotels=hotels, day=0)
    column_values = [r.getValue() * (1 + owen_values[r]) if r in owen_values else '-' for r in all_room_ids]


    df_prices["Room Type"] = [str(r.getFeature(CONSTANTS.FEATURES.TYPE)) for r in all_room_ids]
    df_prices["Room Id"] = [str(r.id) for r in all_room_ids]
    df_prices["Hotel Id"] = [str(r.getHotelId()) for r in all_room_ids]
    df_prices["Init Day"] = column_values

    column_values = [r.getValue() * (1 + constant_incr) if r in owen_values else '-' for r in all_room_ids]
    df_prices_constant["Room Type"] = [str(r.getFeature(CONSTANTS.FEATURES.TYPE)) for r in all_room_ids]
    df_prices_constant["Room Id"] = [str(r.id) for r in all_room_ids]
    df_prices_constant["Hotel Id"] = [str(r.getHotelId()) for r in all_room_ids]
    df_prices_constant["Init Day"] = column_values

    column_values = [0 if r in owen_values else '-' for r in all_room_ids]
    df_gain["Room Type"] = [str(r.getFeature(CONSTANTS.FEATURES.TYPE)) for r in all_room_ids]
    df_gain["Room Id"] = [str(r.id) for r in all_room_ids]
    df_gain["Hotel Id"] = [str(r.getHotelId()) for r in all_room_ids]
    df_gain["Init Day"] = column_values

    column_values = [constant_incr if r in owen_values else '-' for r in all_room_ids]
    df_gain_constant["Room Type"] = [str(r.getFeature(CONSTANTS.FEATURES.TYPE)) for r in all_room_ids]
    df_gain_constant["Room Id"] = [str(r.id) for r in all_room_ids]
    df_gain_constant["Hotel Id"] = [str(r.getHotelId()) for r in all_room_ids]
    df_gain_constant["Init Day"] = column_values

    return df_prices,df_prices_constant,df_gain,df_gain_constant