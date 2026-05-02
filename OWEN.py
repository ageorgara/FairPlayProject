from CONSTANTS import FEATURES
def __buildISG(hotels,day):
    nodes = {}
    for h in hotels:
        hotel_type_nodes = {}
        for room_type in FEATURES.OPTIONS[FEATURES.TYPE]["LIST_OF_OPTIONS"]:
            rooms = h.getAvailableRooms(day,room_type)
            n_av_rooms = len(rooms)
            n_bk_rooms = h.getNumberOfReservedRooms(day,room_type)
            type_node_id = f"{h.id}_{room_type}"
            for room in rooms:
                room_to_type_edge = (n_bk_rooms/(n_av_rooms+n_bk_rooms)) * (1/n_av_rooms)
                nodes[room] = [room_to_type_edge]
                if type_node_id not in nodes:
                    nodes[type_node_id] = []
                nodes[type_node_id].append(room_to_type_edge)
                hotel_type_nodes[type_node_id] = [n_av_rooms,n_bk_rooms]
        for type_1 in hotel_type_nodes:
            extra_node_1 = f"{h.id}_{type_1}"
            if extra_node_1 not in nodes:
                nodes[extra_node_1] = []
            for type_2 in hotel_type_nodes:
                extra_node_2 = f"{h.id}_{type_2}"
                if extra_node_2 not in nodes:
                    nodes[extra_node_2] = []
                if type_1 != type_2:
                    internal_type_to_type_edge = (hotel_type_nodes[type_1][1] + hotel_type_nodes[type_2][1]) / (sum(hotel_type_nodes[type_1])+sum(hotel_type_nodes[type_2]))
                    nodes[extra_node_1].append(internal_type_to_type_edge)
                    nodes[extra_node_2].append(internal_type_to_type_edge)

    for room_type in FEATURES.OPTIONS[FEATURES.TYPE]["LIST_OF_OPTIONS"]:
        for h1 in hotels:
            extra_node_1 = f"{h1.id}_{room_type}"
            if extra_node_1 in nodes:
                n_tot_rooms_1 = h1.getNumberOfRooms(room_type)
                n_bk_rooms_1  = h1.getNumberOfReservedRooms(day, room_type)
                for h2 in hotels:
                    extra_node_2 = f"{h2.id}_{room_type}"
                    if extra_node_2 in nodes and extra_node_1!=extra_node_2:
                        n_tot_rooms_2 = h2.getNumberOfRooms(room_type)
                        n_bk_rooms_2  = h2.getNumberOfReservedRooms(day, room_type)
                        external_type_to_type_edge = (n_bk_rooms_1+n_bk_rooms_2) / (n_tot_rooms_1+n_tot_rooms_2)
                        nodes[extra_node_1].append(external_type_to_type_edge)
                        nodes[extra_node_2].append(external_type_to_type_edge)
    return nodes



def computeOwenValues(hotels,day):
    isg = __buildISG(hotels,day)
    all_edges = sum([sum(isg[node]) for node in isg])
    owen_values = {}
    for h in hotels:
        for room_type in FEATURES.OPTIONS[FEATURES.TYPE]["LIST_OF_OPTIONS"]:
            type_node = f"{h.id}_{room_type}"
            rooms = h.getAvailableRooms(day=day,room_type=room_type)
            n_av_rooms = len(rooms)
            for r in rooms:
                if r not in isg:
                    print(f"Couldn't find room {r} in the graph!")
                else:
                    ow = sum(isg[r])/2 + (sum(isg[type_node])/2)/n_av_rooms
                    owen_values[r] = ow
                    if all_edges>0:
                        owen_values[r] = ow #/all_edges
    return owen_values

def computeOwenValues__(hotels,day):
    owen_values = {}
    total_game_value = 0
    for h in hotels:
        for room_type in FEATURES.OPTIONS[FEATURES.TYPE]["LIST_OF_OPTIONS"]:
            n_av_rooms_rt = h.getNumberOfAvailableRooms(day, room_type)
            if n_av_rooms_rt>0:
                n_bk_rooms_rt = h.getNumberOfReservedRooms(day, room_type)
                owen_room = (1/n_av_rooms_rt) * (n_bk_rooms_rt / (n_av_rooms_rt+n_bk_rooms_rt) )

                internal_pairwise = 0
                for room_type_prime in FEATURES.OPTIONS[FEATURES.TYPE]["LIST_OF_OPTIONS"]:
                    if room_type_prime != room_type:
                        n_av_rooms_rt_prime = h.getNumberOfAvailableRooms(day, room_type_prime)
                        if n_av_rooms_rt_prime > 0:
                            n_bk_rooms_rt_prime = h.getNumberOfReservedRooms(day, room_type_prime)
                            val = (n_bk_rooms_rt+n_bk_rooms_rt_prime)/(n_av_rooms_rt+n_av_rooms_rt_prime+n_bk_rooms_rt+n_bk_rooms_rt_prime)
                            internal_pairwise += val
                internal_pairwise = internal_pairwise/(2*n_av_rooms_rt)
                external_pairwise = 0
                for h_prime in hotels:
                    if h_prime!=h:
                        n_av_rooms_rt_prime = h.getNumberOfAvailableRooms(day, room_type)
                        if n_av_rooms_rt_prime > 0:
                            n_bk_rooms_rt_prime = h.getNumberOfReservedRooms(day, room_type)
                            val = (n_bk_rooms_rt + n_bk_rooms_rt_prime) / ( n_av_rooms_rt + n_av_rooms_rt_prime + n_bk_rooms_rt + n_bk_rooms_rt_prime)
                            external_pairwise += val
                external_pairwise = external_pairwise / (2 * n_av_rooms_rt)
                for r in h.getAvailableRooms(day,room_type):
                    owen_values[r] = owen_room + internal_pairwise+external_pairwise
    mx = max(owen_values.values())
    return owen_values


