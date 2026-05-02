import pandas as pd

from Hotel import Hotel
import CONSTANTS
# from OWEN import computeOwenValues__ as COV
from OWEN import computeOwenValues as COV
from dfUtils import *
import os
import random
from random import shuffle, randint, choice, sample, choices
# import pandas as pd
import json
import numpy as np
from math import ceil
import copy
import pickle
from plots import plotHotelIncome, plotPolicyOccupancy, plotUserService, plotWinningScores, plotAccumulativeHotelIncome, plotAccumulativePolicyOccupancy

'''TO DO: next rmd'''
# def __next(rmd:int, dist:int=1):
#     if rmd>6 or rmd<0:
#         print(f"{rmd} is not valid; interpreted as 0.")
#         retval = 6
#     else:
#         e = 6-rmd+dist
#         retval = rmd+dist if e<=6 else 7-e
#     return  retval

def prev(rmd:int, dist:int=1):
    if rmd>6 or rmd<0:
        print(f"{rmd} is not valid; interpreted as 0.")
        retval = 0
    else:
        e = dist-rmd
        retval = rmd-dist if e<=0 else 7-e
    return  retval

class Simulation:
    def __init__(self, input_file, simulation_period=90, max_reservations_per_day=100, cancellation_probability=0.1,
                 constant_incr_policy=[CONSTANTS.PRICING_POLICIES.SEVENTEEN_PRC], certified=False, score={},
                 iterations=1, mute=False, daily_write=True, output_folder=None, week_shift=0,
                 sunday = 0
                 ):
        self.simulation_period = simulation_period
        self.__day_prob = {"high":0.95,"med":0.6,"low":0.1}
        self.max_reservations_per_day = max_reservations_per_day
        self.cancellation_probability = cancellation_probability
        self.constant_incr_policy = constant_incr_policy
        self.certified = certified
        self.certified_label = "Certified" if self.certified else "Non-Certified"
        self.score = score
        self.iterations = iterations
        self.mute = mute
        self.daily_write = daily_write
        self.__sunday = sunday
        self.__saturday = prev(self.__sunday,1)
        self.__friday = prev(self.__sunday,2)
        self.__thursday = prev(self.__sunday,3)
        self.__wednesday = prev(self.__sunday,4)
        self.__tuesday = prev(self.__sunday,5)
        self.__monday = prev(self.__sunday,6)
        print(f"Sunday {self.__sunday}\t Saturday {self.__saturday}\t Friday {self.__friday}\n"
              f"Thursday{self.__thursday}\tWednesday{self.__wednesday}\tTuesday{self.__tuesday}\tMonday{self.__monday}")
        self.week = {
            "high" : [i for i in range(self.simulation_period) if (i+week_shift)%7 in [self.__sunday, self.__saturday,self.__friday]],
            "med"  : [i for i in range(self.simulation_period) if (i+week_shift)%7 in [self.__thursday]],
            "low"  : [i for i in range(self.simulation_period) if (i+week_shift)%7 in [self.__tuesday, self.__wednesday,self.__monday]]
        }

        self.filename = input_file.split('/')[-1].split('.csv')[0]
        if output_folder:
            self.output_folder = output_folder
        else:
            self.output_folder = f"Results/{self.filename}/{simulation_period} days/cancellation probability \
{self.cancellation_probability}/{max_reservations_per_day} max reservations per day"
        os.makedirs(self.output_folder, exist_ok=True)
        self.hotels = Hotel.loadHotelsCSV(input_file, time_period=simulation_period)
        self.__prepareINFOholders()
        #
        self.__booking_window = 7
        self.__max_rho_index = 1e+10
        self.__prc_to_show = 0.3
        self.__beta = {
            CONSTANTS.PRICING_POLICIES.SEVENTEEN_PRC : 10,
            CONSTANTS.PRICING_POLICIES.TWENTY_PRC : 50,
            CONSTANTS.PRICING_POLICIES.FORTY_PRC : 5,
            CONSTANTS.PRICING_POLICIES.FIFTY_PRC : 2,
            CONSTANTS.PRICING_POLICIES.SIXTY_PRC : 5,
            CONSTANTS.PRICING_POLICIES.SEVENTY_PRC : 5,
            CONSTANTS.PRICING_POLICIES.HUNDRED_PRC : 2,
            CONSTANTS.PRICING_POLICIES.TWO_HUNDRED_PRC : 2,
        }
        self.__room_selecting_policy = "min"
        #
        self.__current_iteration = 0
        self.__current_num_of_reservations_made = 0

    def __prepareINFOholders(self):
        self.df_hotel_gain_avg_non = prepareIncomeSimulationDF(self.hotels, self.simulation_period)
        self.df_hotel_gain_avg_partially = prepareIncomeSimulationDF(self.hotels, self.simulation_period)
        self.df_hotel_gain_avg_fully = prepareIncomeSimulationDF(self.hotels, self.simulation_period)
        self.df_occupancy_rate_avg = prepareOccupancySimulationDF(self.hotels, self.simulation_period)
        self.winning_scores = {p: 0 for p in CONSTANTS.PRICING_POLICIES.DEFAULT_POLICIES}
        self.reservations_per_profile = {
            u: {
                p: {"searched": 0, "reserved": 0} for p in self.winning_scores} for u in
            CONSTANTS.USER_PROFILES.USER_PROFILES.keys()
        }
        self.df_avg_room_price = preparePricesSimulationDF(self.hotels, self.simulation_period)
        self.room_price_counters = {day:{r.id:1 for h in self.hotels for r in h.rooms} for day in range(self.simulation_period)}
        self.__RDFS = {
            "non":self.df_hotel_gain_avg_non,
            "partially": self.df_hotel_gain_avg_partially,
            "fully": self.df_hotel_gain_avg_fully
        }
        #
        self.df_hotel_gain_non_all_values = prepareIncomeSimulationAccumulateDF(self.simulation_period)
        self.df_hotel_gain_partially_all_values = prepareIncomeSimulationAccumulateDF(self.simulation_period)
        self.df_hotel_gain_fully_all_values = prepareIncomeSimulationAccumulateDF(self.simulation_period)
        self.df_occupancy_rate_avg_all = prepareIncomeSimulationAccumulateDF(self.simulation_period)
        self.df_occupancy_share_avg_all = prepareIncomeSimulationAccumulateDF(self.simulation_period)
        self.__hotelIDs_per_PP = {}
        for h in self.hotels:
            if h.getPricingPolicy() not in self.__hotelIDs_per_PP:
                self.__hotelIDs_per_PP[h.getPricingPolicy()] = []
            self.__hotelIDs_per_PP[h.getPricingPolicy()].append(h.id)

        # old simulation dfs
        self.df_FairPlay_price, self.df_Static_price, self.df_FairPlay_gain, self.df_Static_gain = preparePriceCompareDF(
            self.simulation_period, self.hotels, self.constant_incr_policy[0])


    def setBookingWindow(self,window):
        self.__booking_window = window

    def getCurrentIteration(self):
        return self.__current_iteration
    def getTotalNumberOfReservations(self):
        return self.__current_num_of_reservations_made

    def iterate(self):
        self.__iterate(0,self.iterations)

    def simplesimulateCMP(self, constant_incr):
        # just one iteration
        reservations = {day: [] for day in range(self.simulation_period)}
        all_room_ids = [r for h in self.hotels for r in h.rooms]
        for day in range(self.simulation_period):
            reservations = self.simulateSimple(day, reservations)
            owen_values = COV(self.hotels, day)

            column_values = [r.getValue() * (1 + owen_values[r]) if r in owen_values else '-' for r in all_room_ids]
            column_values_constant = [r.getValue() * (1 + constant_incr) if r in owen_values else '-' for r in
                                      all_room_ids]

            self.df_FairPlay_price["Day " + str(day + 1)] = column_values
            self.df_Static_price["Day " + str(day + 1)] = column_values_constant

            column_values = [r.getValue() * (1 + owen_values[r]) if r in owen_values else '-' for r in all_room_ids]
            column_values_constant = [r.getValue() * constant_incr if r in owen_values else '-' for r in all_room_ids]

            self.df_FairPlay_gain["Day " + str(day + 1)] = column_values
            self.df_Static_gain["Day " + str(day + 1)] = column_values_constant

        self.writeSimple()


    def resume_itarate(self,start_iteration,iterations=None):
        if iterations==None:
            iterations = max([0,self.iterations-start_iteration])
        self.__iterate(start_iteration, iterations)


    def __iterate(self,start_iteration,iterations):
        for iteration in range(start_iteration, start_iteration+iterations):
            random.seed(iteration)
            np.random.seed(iteration)
            Hotel.freeAll(self.hotels)
            print(f">>>Iteration {iteration}<<<")
            shuffle(self.hotels)
            total_number_of_reservations_made = 0
            reservations = {day : [] for day in range(self.simulation_period)}
            new_row = {
                "gain":{
                    "non" :{
                        p : {"Iteration":iteration,"Pricing Policy":p, "Init Day":0} for p in self.__hotelIDs_per_PP
                    },
                    "fully": {
                        p : {"Iteration":iteration,"Pricing Policy":p, "Init Day":0} for p in self.__hotelIDs_per_PP
                    },
                    "partially":{
                        p: {"Iteration":iteration,"Pricing Policy": p, "Init Day": 0} for p in self.__hotelIDs_per_PP
                    }
                },
                "occupancy":{
                    "rate": {
                        p : {"Iteration":iteration,"Pricing Policy":p, "Init Day":0} for p in self.__hotelIDs_per_PP
                    },
                    "share" : {
                        p : {"Iteration":iteration,"Pricing Policy":p, "Init Day":0} for p in self.__hotelIDs_per_PP
                    }
                }
            }
            for day in range(self.simulation_period):
                reservations, number_of_reservations, daily_gain = self.simulate(day, reservations)
                total_number_of_reservations_made += number_of_reservations
                owen_values = COV(self.hotels, day)

                # average price per room per hotel
                rids = self.df_avg_room_price["Room Id"].tolist()
                if iteration==0:
                    R = {r.id:r.getValue() if r.getPricingPolicy()==CONSTANTS.PRICING_POLICIES.FAIRPLAY else r.getValue()*(1+CONSTANTS.PRICING_POLICIES.INCREMENT[r.getPricingPolicy()]) for h in self.hotels for r in h.rooms}
                    xx=[R[rid] for rid in rids]
                else:
                    xx = self.df_avg_room_price[f"Day {day+1}"].tolist()
                yy = {
                    r.id: 0 if r not in owen_values else r.getValue()*(1+owen_values[r]) if r.getPricingPolicy() ==
                    CONSTANTS.PRICING_POLICIES.FAIRPLAY else r.getValue()*(1+CONSTANTS.PRICING_POLICIES.INCREMENT[r.getPricingPolicy()])
                    for h in self.hotels for r in h.rooms
                }
                column_values = [
                    xx[i] + yy[ rids[i] ] for i in range(len(rids))
                ]
                fr = [r.id for h in self.hotels for r in h.getAvailableRooms(day=day)]
                self.df_avg_room_price[f"Day {day+1}"] = column_values
                for rid in fr:
                    self.room_price_counters[day][rid] += 1

                # average gain per hotel
                for refund_policy in self.__RDFS:
                    df = self.__RDFS[refund_policy]
                    hids = df["Hotel Id"].tolist()
                    if day==0:
                        xx = df["Init Day"].tolist()
                    else:
                        xx = df[f"Day {day}"].tolist()
                    column_values = [
                        xx[i] + daily_gain[hids[i]][refund_policy] for i in range(len(hids))
                    ]
                    df[f"Day {day+1}"] = column_values
                    for pricing_policy in self.__hotelIDs_per_PP:
                        if day == 0:
                            prev = 0
                        else:
                            prev = new_row["gain"][refund_policy][pricing_policy][f"Day {day}"]
                        val = sum([daily_gain[hid][refund_policy] for hid in self.__hotelIDs_per_PP[pricing_policy]])
                        new_row["gain"][refund_policy][pricing_policy][f"Day {day+1}"] = prev+val


                #     average occupancy rate
                hids = self.df_occupancy_rate_avg["Hotel Id"].tolist()
                total_reserved = {h.id: h.getNumberOfReservedRooms(day=day) for h in self.hotels}
                if iteration==0:
                    xx = [0 for hid in hids]
                else:
                    xx = self.df_occupancy_rate_avg[f"Day {day+1}"]
                column_values = [
                    xx[i] + total_reserved[hids[i]] for i in range(len(hids))
                ]
                self.df_occupancy_rate_avg[f"Day {day+1}"] = column_values
                stotal_reserved = sum(total_reserved.values())
                for pricing_policy in self.__hotelIDs_per_PP:
                    reserved = sum([h.getNumberOfReservedRooms(day=day) for h in self.hotels if h.id in self.__hotelIDs_per_PP[pricing_policy]])
                    total = sum([h.getNumberOfRooms() for h in self.hotels if h.id in self.__hotelIDs_per_PP[pricing_policy]])
                    new_row["occupancy"]["rate"][pricing_policy][f"Day {day+1}"] = float(reserved) / total
                    new_row["occupancy"]["share"][pricing_policy][f"Day {day +1}"] = float(reserved) / stotal_reserved if stotal_reserved>0 else 0

            for pricing_policy in self.__hotelIDs_per_PP:
                self.df_hotel_gain_non_all_values = self.df_hotel_gain_non_all_values._append(new_row["gain"]["non"][pricing_policy],ignore_index = True)
                self.df_hotel_gain_fully_all_values = self.df_hotel_gain_fully_all_values._append(new_row["gain"]["fully"][pricing_policy],ignore_index = True)
                self.df_hotel_gain_partially_all_values = self.df_hotel_gain_partially_all_values._append(new_row["gain"]["partially"][pricing_policy],ignore_index = True)
                self.df_occupancy_rate_avg_all = self.df_occupancy_rate_avg_all._append(new_row["occupancy"]["rate"][pricing_policy],ignore_index = True)
                self.df_occupancy_share_avg_all = self.df_occupancy_share_avg_all._append(new_row["occupancy"]["share"][pricing_policy],ignore_index = True)

            self.__current_iteration = iteration + 1
            self.__current_num_of_reservations_made += total_number_of_reservations_made
            self.write(iteration+1, total_number_of_reservations_made)
            self.save()

    def simulate(self, day, reservations):
        daily_gain = {h.id: {"non":0,"partially":0,"fully":0} for h in self.hotels}
        reservations_dates = list(
            range(day, min([day + self.__booking_window, self.simulation_period]))
        )
        reservations_date_weights = {
            d:self.__day_prob["high"] if d in self.week["high"] else self.__day_prob["med"] if d in self.week["med"] else self.__day_prob["low"]
            for d in reservations_dates
        }
        ss = sum(reservations_date_weights.values())
        reservations_date_weights = {d:reservations_date_weights[d]/ss for d in reservations_date_weights}
        available_rooms_until_end_of_period = sum(
            [
                sum(
                    [h.getNumberOfAvailableRooms(d) for h in self.hotels]
                ) for d in reservations_dates
            ]
        )

        # day 0 is Sunday
        rmd = day % 7
        if rmd == self.__sunday or rmd ==self.__saturday:
            ub = min([self.max_reservations_per_day, available_rooms_until_end_of_period])
            lb = int(0.9*ub)
        elif rmd == self.__friday:
            ub = min([self.max_reservations_per_day, available_rooms_until_end_of_period])
            lb = int(0.7*ub)
        else:
            ub = min([int(0.75*self.max_reservations_per_day), available_rooms_until_end_of_period])
            lb = 0
        number_of_reservations = randint(lb,ub)
        # number_of_reservations = randint(0, min([self.max_reservations_per_day, available_rooms_until_end_of_period]))
        DNR = number_of_reservations
        while number_of_reservations:
            if not self.mute:
                print(f'\t{number_of_reservations} reservations yet to make...')
            # Picking reservation date
            # checkin_date = choice(reservations_dates)

            checkin_date = choices(reservations_dates, weights=reservations_date_weights, k=1)[0]
            available_room_types = [r.getFeature(CONSTANTS.FEATURES.TYPE) for h in self.hotels for r in
                                    h.getAvailableRooms(checkin_date)]
            if len(available_room_types) == 0:
                continue
            desired_room_type = choice(available_room_types)
            owen_values = COV(hotels=self.hotels, day=checkin_date)

            reservation, daily_gain = self.__makeNewReservation(checkin_date=checkin_date,room_type=desired_room_type,
                                                                owen_values=owen_values,daily_gain=daily_gain)
            if reservation == -1:
                continue
            if reservation:
                reservations[checkin_date].append(reservation)
            number_of_reservations -= 1
            if random.random() <= self.cancellation_probability:
                cancellation_date = choice(reservations_dates)
                if reservations[cancellation_date]:
                    if not self.mute:
                        print(f'\t\t==>Cancelling reservation on Day {cancellation_date}<==')
                    reservation = choice(reservations[cancellation_date])
                    hotel_id = reservation.hotel_id
                    partially_refund_value = reservation.price / 2
                    fully_refund_value = reservation.price
                    non_refund_value = 0
                    reservation.cancel()
                    daily_gain[hotel_id]["non"] -= non_refund_value
                    daily_gain[hotel_id]["partially"] -= partially_refund_value
                    daily_gain[hotel_id]["fully"] -= fully_refund_value
                    reservations[cancellation_date].remove(reservation)
        return reservations, DNR, daily_gain

    def simulateSimple(self, day, reservations):
        daily_gain = {h.id: {"non":0,"partially":0,"fully":0} for h in self.hotels}
        reservations_dates = list(
            range(day, self.simulation_period)
        )
        # reservations_date_weights = {d:self.__day_prob["high"] if d in self.week["high"] else self.__day_prob["low"] for d in reservations_dates}
        # ss = sum(reservations_date_weights.values())
        # reservations_date_weights = {d:reservations_date_weights[d]/ss for d in reservations_date_weights}
        available_rooms_until_end_of_period = sum(
            [
                sum(
                    [h.getNumberOfAvailableRooms(d) for h in self.hotels]
                ) for d in reservations_dates
            ]
        )
        # day 0 is Sunday
        rmd = day % 7
        if rmd == 0 or rmd ==6:
            ub = min([self.max_reservations_per_day, available_rooms_until_end_of_period])
            lb = int(0.9*ub)
        elif rmd == 5:
            ub = min([self.max_reservations_per_day, available_rooms_until_end_of_period])
            lb = int(0.7*ub)
        else:
            ub = min([int(0.75*self.max_reservations_per_day), available_rooms_until_end_of_period])
            lb = 0

        number_of_reservations = randint(lb,ub)
        # number_of_reservations = randint(0, min([self.max_reservations_per_day, available_rooms_until_end_of_period]))

        while number_of_reservations:
            if not self.mute:
                print(f'\t{number_of_reservations} reservations yet to make...')
            # Picking reservation date
            # checkin_date = choice(reservations_dates)

            # checkin_date = choices(reservations_dates, weights=reservations_date_weights, k=1)[0]
            checkin_date = choice(reservations_dates)
            available_room_types = [r.getFeature(CONSTANTS.FEATURES.TYPE) for h in self.hotels for r in
                                    h.getAvailableRooms(checkin_date)]
            if len(available_room_types) == 0:
                continue
            desired_room_type = choice(available_room_types)
            owen_values = COV(hotels=self.hotels, day=checkin_date)
            # ###############
            hotels_to_show = self.__findRoomsToShow(owen_values=owen_values,
                                                    checkin_date=checkin_date,
                                                    room_type=desired_room_type
                                                    )
            if not hotels_to_show:
                continue

            idx = choice(hotels_to_show)
            selected_room = self.hotels[idx].findRoom(room_type=desired_room_type, day=checkin_date)
            # price = selected_room.getValue() * (1 + owen_values[selected_room])
            reservation = self.hotels[idx].bookRoom(day=checkin_date, roomType=desired_room_type,
                                                        increment=owen_values[selected_room])

            if reservation == -1:
                continue
            if reservation:
                reservations[checkin_date].append(reservation)
            number_of_reservations -= 1
            if random.random() <= self.cancellation_probability:
                cancellation_date = choice(reservations_dates)
                if reservations[cancellation_date]:
                    if not self.mute:
                        print(f'\t\t==>Cancelling reservation on Day {cancellation_date}<==')
                    reservation = choice(reservations[cancellation_date])
                    reservation.cancel()
                    reservations[cancellation_date].remove(reservation)
        return reservations
    def __makeNewReservation(self, checkin_date, room_type, owen_values, daily_gain):
        user_profile = choice(list(CONSTANTS.USER_PROFILES.USER_PROFILES.keys()))
        max_budget = CONSTANTS.USER_PROFILES.USER_PROFILES[user_profile]

        hotels_to_show = self.__findRoomsToShow(owen_values=owen_values,
                                                checkin_date=checkin_date,
                                                room_type=room_type
                                                )
        if not hotels_to_show:
            return -1, daily_gain

        idx = self.__pickHotel(idxs=hotels_to_show, room_type=room_type,
                               owen_values=owen_values, day=checkin_date)

        selected_room = self.hotels[idx].findRoom(room_type=room_type, day=checkin_date)
        selected_pricing_policy = self.hotels[idx].getPricingPolicy()
        if selected_pricing_policy == CONSTANTS.PRICING_POLICIES.FAIRPLAY:
            increment = owen_values[selected_room]
        else:
            increment = CONSTANTS.PRICING_POLICIES.INCREMENT[selected_pricing_policy]
        self.reservations_per_profile[user_profile][selected_pricing_policy]["searched"] += 1
        price = selected_room.getValue() * (1 + increment)
        reservation = None
        if price <= max_budget:
            if not self.mute:
                print(
                    f'\t\t==>Reserving room of type {room_type} at {self.hotels[idx]} with price {price} \
(policy {self.hotels[idx].getPricingPolicy()})<=='
                )
            self.reservations_per_profile[user_profile][selected_pricing_policy]["reserved"] += 1
            daily_gain[self.hotels[idx].id]["non"] += price
            daily_gain[self.hotels[idx].id]["partially"] += price
            daily_gain[self.hotels[idx].id]["fully"] += price

            reservation = self.hotels[idx].bookRoom(day=checkin_date, roomType=room_type,
                                                    increment=increment)
        return reservation,daily_gain

    def __findRoomsToShow(self, owen_values, checkin_date, room_type):
        available_hotels = [h for h in self.hotels if h.getNumberOfAvailableRooms(checkin_date, room_type) > 0]
        shuffle(available_hotels)
        owen_per_hotel = {
            h.id: sum([owen_values[r] for r in h.rooms if r.isfree(checkin_date)]) for h in
            available_hotels
        }
        rho_index = {
            h: self.__max_rho_index if owen_per_hotel[h.id] == 0 else h.getExposureCounter() / owen_per_hotel[h.id]
            for h in available_hotels
        }
        number_of_hotels_to_show = ceil(self.__prc_to_show * len(available_hotels))
        if self.certified:
            rho_index_inverse = {
                h: 1 / rho_index[h] if rho_index[h] > 0 else self.__max_rho_index for h in available_hotels
            }
            gamma = 1 / sum(rho_index_inverse.values())
            probability = {}
            for h in available_hotels:
                p = rho_index_inverse[h] * gamma
                if h.getPricingPolicy() != CONSTANTS.PRICING_POLICIES.FAIRPLAY:
                    r = h.findRoom(room_type=room_type, day=checkin_date)

                    alpha = CONSTANTS.PRICING_POLICIES.INCREMENT[r.getPricingPolicy()]
                    alpha_CF = owen_values[r]
                    beta = min([1, (1+alpha_CF) / (1 + alpha)])
                    p *= beta

                    # OLD CODE 1/10/2025
                    # beta = min([1 / alpha, (1 + alpha * owen_values[r]) / (1 + owen_values[r])])
                    # p *= beta * (1 + owen_values[r]) / (1 + alpha * owen_values[r])
                    # OLD CODE 1/9/2025
                    # p_ncf = (1 + owen_values[r]) / (1 + CONSTANTS.PRICING_POLICIES.INCREMENT[r.getPricingPolicy()])
                    # beta = max([self.__beta[h.getPricingPolicy()], 1 / p_ncf])
                    # p *= p_ncf * (1 + 1 / beta)
                probability[h] = p
            keys = list(probability.keys())
            values = list(probability.values())
            sorted_value_index = np.argsort(values)
            val_keys = {val: [key for key in keys if probability[key] == values[val]] for val in sorted_value_index}
            max_val = sorted_value_index[-1]
            # max_val = sorted_value_index[0]

            if len(val_keys[max_val]) < number_of_hotels_to_show:
                hotels2show = [self.hotels.index(keys[i]) for i in sorted_value_index[-number_of_hotels_to_show:]]
                # hotels2show = [self.hotels.index(keys[i]) for i in sorted_value_index[:number_of_hotels_to_show]]
            else:
                hotels2show = [self.hotels.index(key) for key in sample(val_keys[max_val], number_of_hotels_to_show)]
        else:
            keys = list(rho_index.keys())
            values = list(rho_index.values())
            sorted_value_index = np.argsort(values)

            hotels2show = [self.hotels.index(keys[i]) for i in sorted_value_index[:number_of_hotels_to_show]]
        for idx in hotels2show:
            self.hotels[idx].exposed()

        return hotels2show

    def __pickHotel(self, idxs, room_type, owen_values, day):
        shown_hotels = [self.hotels[i] for i in idxs]
        rooms = [h.findRoom(room_type=room_type, day=day) for h in shown_hotels]
        shuffle(rooms)
        prices = [r.getValue() * (
                1 + owen_values[r]) if r.getPricingPolicy() == CONSTANTS.PRICING_POLICIES.FAIRPLAY else r.getValue() * (
                1 + CONSTANTS.PRICING_POLICIES.INCREMENT[r.getPricingPolicy()]) for r in rooms]
        k = len(prices)
        if self.__room_selecting_policy == "min":
            sorted_prices = sorted(prices)
        elif self.__room_selecting_policy == "max":
            sorted_prices = sorted(prices, reverse=True)
        else:
            avg = sum(prices) / k
            sorted_prices = sorted(prices, key=lambda x: abs(x - avg))
        val = sorted_prices[0]
        selections = [idx for idx in range(len(prices)) if prices[idx]==val]
        # idx = prices.index(val)
        idx = choice(selections)

        for i in range(k):
            hidx = prices.index(sorted_prices[i])
            pp = shown_hotels[hidx].getPricingPolicy()
            self.winning_scores[pp] += (k - i + 1) / k
        return idxs[idx]

    def write(self,iteration,number_or_reservations):
        # normalize with repetition
        df = copy.deepcopy(self.df_avg_room_price)
        for day in range(self.simulation_period):
            df["Daily counter"] = [self.room_price_counters[day][rid] for rid in df["Room Id"].tolist()]
            df[f"Day {day+1}"] = df.apply( lambda x: x[f"Day {day+1}"] / x["Daily counter"], axis=1)
        df = df.drop("Daily counter", axis=1)
        df.to_csv(f"{self.output_folder}/{self.certified_label}___Average Room Prices.csv",index=False)


        for refunding_policy in self.__RDFS:
            df = copy.deepcopy(self.__RDFS[refunding_policy])

            unique_polices = df["Pricing Policy"].unique().tolist()
            # acc_df = pd.DataFrame(
                # columns=["Pricing Policy", "Init Day"] + ["Day " + str(d + 1) for d in range(self.simulation_period)])
            for day in range(self.simulation_period):
                df[f"Day {day+1}"] = df[f"Day {day+1}"].apply(lambda x: x/iteration)

            df.to_csv(f"{self.output_folder}/{self.certified_label}___Average Income ({refunding_policy} refundable).csv",index=False)
            plotHotelIncome(df,
                            filename=f"{self.output_folder}/{self.certified_label}___Average Income({refunding_policy} refundable).png",
                            day_idx=3)
            df = df.drop("Hotel Id", axis=1)
            acc_df = df.groupby(['Pricing Policy']).sum()
            acc_df = acc_df.reset_index()
            acc_df.to_csv(f"{self.output_folder}/{self.certified_label}___Average Accumulative Income ({refunding_policy} refundable).csv",index=False)
            plotAccumulativeHotelIncome(acc_df,
                            filename=f"{self.output_folder}/{self.certified_label}___Average Accumulative Income({refunding_policy} refundable).png",
                            day_idx=2)


        df = copy.deepcopy(self.df_occupancy_rate_avg)
        for day in range(self.simulation_period):
            df[f"Day {day+1}"] = df[f"Day {day+1}"].apply(lambda x: x / iteration)
            # df[f"Day {day+1}"] = df.apply(lambda x: x[f"Day {day+1}"] / x["Total Number of Rooms"]*iteration, axis=1)
        df.to_csv(f"{self.output_folder}/{self.certified_label}___Average Occupancy Rate.csv", index=False)
        plotPolicyOccupancy(df, filename=f"{self.output_folder}/{self.certified_label}___Average Occupancy Rate.png",
                            day_idx=3)
        ################################################################################################################
        # df = copy.deepcopy(self.df_occupancy_rate_avg)
        # for day in range(self.simulation_period):
        #     total_counter = sum(h.getNumberOfReservedRooms(day) for h in self.hotels)
        #     if total_counter==0:
        #         df[f"Day {day + 1}"] = df.apply(lambda x: 0)
        #     else:
        #         df[f"Day {day + 1}"] = df.apply(lambda x: x[f"Day {day + 1}"] / total_counter, axis=1)
        # # df = df.drop("Daily counter", axis=1)
        # df.to_csv(f"{self.output_folder}/{self.certified_label}___Average Occupancy Share.csv", index=False)
        # plotPolicyOccupancy(df, filename=f"{self.output_folder}/{self.certified_label}___Average Occupancy Share.png",
        #                     day_idx=3)
        ################################################################################################################
        ################################################################################################################
        # plotting new averages:
        df = copy.deepcopy(self.df_hotel_gain_non_all_values)
        acc_df = df.groupby(["Pricing Policy"]).mean()
        acc_df = acc_df.reset_index()
        self.df_hotel_gain_non_all_values.to_csv(
            f"{self.output_folder}/{self.certified_label}___Average Accumulative Income (non refundable)__all iterations.csv",
            index=False
        )
        acc_df.to_csv(
            f"{self.output_folder}/{self.certified_label}___Average Accumulative Income (non refundable)__new.csv",
            index=False)
        plotAccumulativeHotelIncome(acc_df,
                                    filename=f"{self.output_folder}/{self.certified_label}___Average Accumulative Income(non refundable)__new.png",
                                    day_idx=2)
        df = copy.deepcopy(self.df_hotel_gain_fully_all_values)
        acc_df = df.groupby(["Pricing Policy"]).mean()
        acc_df = acc_df.reset_index()
        self.df_hotel_gain_fully_all_values.to_csv(
            f"{self.output_folder}/{self.certified_label}___Average Accumulative Income (fully refundable)__all iterations.csv",
            index=False
        )
        acc_df.to_csv(
            f"{self.output_folder}/{self.certified_label}___Average Accumulative Income (fully refundable)__new.csv",
            index=False)
        plotAccumulativeHotelIncome(acc_df,
                                    filename=f"{self.output_folder}/{self.certified_label}___Average Accumulative Income(fully refundable)__new.png",
                                    day_idx=2)
        df = copy.deepcopy(self.df_hotel_gain_partially_all_values)
        acc_df = df.groupby(["Pricing Policy"]).mean()
        acc_df = acc_df.reset_index()
        self.df_hotel_gain_partially_all_values.to_csv(
            f"{self.output_folder}/{self.certified_label}___Average Accumulative Income (partially refundable)__all iterations.csv",
            index=False
        )
        acc_df.to_csv(
            f"{self.output_folder}/{self.certified_label}___Average Accumulative Income (partially refundable)__new.csv",
            index=False)
        plotAccumulativeHotelIncome(acc_df,
                                    filename=f"{self.output_folder}/{self.certified_label}___Average Accumulative Income(partially refundable)__new.png",
                                    day_idx=2)

        df = copy.deepcopy(self.df_occupancy_rate_avg_all)
        df = df.drop("Iteration", axis=1)
        acc_df = df.groupby(["Pricing Policy"]).mean()
        acc_df = acc_df.reset_index()
        self.df_occupancy_rate_avg_all.to_csv(
            f"{self.output_folder}/{self.certified_label}___Average Occupancy Rate__all iterations.csv",
            index=False
        )
        acc_df.to_csv(
            f"{self.output_folder}/{self.certified_label}___Average Occupancy Rate__new.csv",
            index=False)
        plotAccumulativePolicyOccupancy(acc_df,
                                    filename=f"{self.output_folder}/{self.certified_label}___Average Occupancy Rate__new.png",
                                    day_idx=2)

        df = copy.deepcopy(self.df_occupancy_share_avg_all)
        df = df.drop("Iteration", axis=1)
        acc_df = df.groupby(["Pricing Policy"]).mean()
        acc_df = acc_df.reset_index()
        self.df_occupancy_share_avg_all.to_csv(
            f"{self.output_folder}/{self.certified_label}___Average Occupancy Share__all iterations.csv",
            index=False
        )
        acc_df.to_csv(
            f"{self.output_folder}/{self.certified_label}___Average Occupancy Share__new.csv",
            index=False)
        plotAccumulativePolicyOccupancy(acc_df,
                                    filename=f"{self.output_folder}/{self.certified_label}___Average Occupancy Share__new.png",
                                    day_idx=2)
        ################################################################################################################

        data = {pp: self.winning_scores[pp] / iteration for pp in self.winning_scores}
        # data = {pp: data[pp] / number_or_reservations for pp in self.winning_scores}
        plotWinningScores(data, f"{self.output_folder}/{self.certified_label}___Winning Scores.png")
        with open(f"{self.output_folder}/{self.certified_label}___Winning Scores.json","w") as f:
            json.dump(data, f, indent=4)

        data = {}
        for user_profile in self.reservations_per_profile:
            data[user_profile]= {}
            for pp in self.reservations_per_profile[user_profile]:
                if self.reservations_per_profile[user_profile][pp]["searched"]>0:
                    data[user_profile][pp] = self.reservations_per_profile[user_profile][pp]["reserved"]/self.reservations_per_profile[user_profile][pp]["searched"]
                else:
                    data[user_profile][pp] = 0
                # data[user_profile][pp] /= number_or_reservations
        plotUserService(data, f"{self.output_folder}/{self.certified_label}___User service.png")
        with open(f"{self.output_folder}/{self.certified_label}___User service.json","w") as f:
            json.dump(data, f, indent=4)

    def plot(self,iteration):
        for refunding_policy in self.__RDFS:
            df = copy.deepcopy(self.__RDFS[refunding_policy])
            for day in range(self.simulation_period):
                df[f"Day {day + 1}"] = df[f"Day {day + 1}"].apply(lambda x: x / iteration)
            plotHotelIncome(df,filename=f"{self.output_folder}/{self.certified_label}___Average Income({refunding_policy} refundable).png",day_idx=3)

        df = copy.deepcopy(self.df_occupancy_rate_avg)
        for day in range(self.simulation_period):
            df[f"Day {day + 1}"] = df[f"Day {day + 1}"].apply(lambda x: x / iteration)
        plotPolicyOccupancy(df,filename=f"{self.output_folder}/{self.certified_label}___Average Occupancy Rate).png",day_idx=3)

        data = {}
        for user_profile in self.reservations_per_profile:
            data[user_profile] = {}
            for pp in self.reservations_per_profile[user_profile]:
                if self.reservations_per_profile[user_profile][pp]["searched"] > 0:
                    data[user_profile][pp] = self.reservations_per_profile[user_profile][pp]["reserved"] / \
                                             self.reservations_per_profile[user_profile][pp]["searched"]
                else:
                    data[user_profile][pp] = 0
        plotUserService(data,f"{self.output_folder}/{self.certified_label}___User service.png")
        data = {pp: self.winning_scores[pp] / iteration for pp in self.winning_scores}
        # data = {pp: data[pp] / number_or_reservations for pp in self.winning_scores}
        plotWinningScores(data,f"{self.output_folder}/{self.certified_label}___Winning Scores.png")

    def writeSimple(self):
        self.df_FairPlay_price.to_csv(f"{self.output_folder}/{self.certified_label}___FairplayPrices.csv")
        self.df_Static_price.to_csv(f"{self.output_folder}/{self.certified_label}___StaticPrices.csv")
        return


    def save(self):
        with open(f"{self.output_folder}/{self.certified_label}_simulation.pkl","wb") as f:
            pickle.dump(self,f,pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def load(file):
        with open(file,"rb") as f:
            return pickle.load(f)

if __name__ == '__main__':
    path = "Results/Non_Identical_FP_vs_+17%_vs_+40%_vs_+50% (medium2 25 vs 25 vs 25 vs 25)/30 days/cancellation probability 0.1/1800 max reservations per day/Certified"
    file = f"{path}_simulation.pkl"
    s = Simulation.load(file)

    df = copy.deepcopy(s.df_occupancy_rate_avg)
    for day in range(s.simulation_period):
        df[f"Day {day + 1}"] = df[f"Day {day + 1}"].apply(lambda x: x / s.iterations)
        # df[f"Day {day+1}"] = df.apply(lambda x: x[f"Day {day+1}"] / x["Total Number of Rooms"], axis=1)
    df.to_csv(f"{s.output_folder}/{s.certified_label}___Average Occupancy Rate.csv", index=False)
    plotPolicyOccupancy(df, filename=f"{s.output_folder}/{s.certified_label}___Average Occupancy Rate (final).png",
                        day_idx=4)