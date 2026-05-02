import matplotlib.pyplot as plt
import os
import CONSTANTS
import numpy as np
LINES = {
    CONSTANTS.PRICING_POLICIES.FAIRPLAY: "-",
    CONSTANTS.PRICING_POLICIES.SEVENTEEN_PRC: ":",
    CONSTANTS.PRICING_POLICIES.FORTY_PRC: "-.",
    CONSTANTS.PRICING_POLICIES.FIFTY_PRC: "--",
    CONSTANTS.PRICING_POLICIES.SIXTY_PRC: "-.",
    CONSTANTS.PRICING_POLICIES.SEVENTY_PRC: "--",
    CONSTANTS.PRICING_POLICIES.HUNDRED_PRC: "--",
    CONSTANTS.PRICING_POLICIES.TWO_HUNDRED_PRC: "--",
    CONSTANTS.PRICING_POLICIES.TWENTY_PRC: (0,(3,10,1,10,1,10))
}

COLORS = {
    CONSTANTS.PRICING_POLICIES.FAIRPLAY: "#1ea300",
    CONSTANTS.PRICING_POLICIES.SEVENTEEN_PRC: "#ff00bf",
    CONSTANTS.PRICING_POLICIES.FORTY_PRC: "#fc9003",
    CONSTANTS.PRICING_POLICIES.FIFTY_PRC: "#cc0c0c",
    CONSTANTS.PRICING_POLICIES.SIXTY_PRC: "#6600ff",
    CONSTANTS.PRICING_POLICIES.SEVENTY_PRC: "#cc0c0c",
    CONSTANTS.PRICING_POLICIES.HUNDRED_PRC: "#cc0c0c",
    CONSTANTS.PRICING_POLICIES.TWO_HUNDRED_PRC: "#cc0c0c",
    CONSTANTS.PRICING_POLICIES.TWENTY_PRC: "#cccc00"
}


def plotHotelIncome(df,filename,day_idx):
    pathfile = "/".join(filename.split("/")[:-1])
    os.makedirs(pathfile, exist_ok=True)
    x_val = df.columns[day_idx:].tolist()
    px = 1 / plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(2560 * px, 997 * px))
    for index, row in df.iterrows():
        name = row["Hotel Id"]
        y_val = [row[d] for d in x_val]
        policy = row["Pricing Policy"]
        line_style = LINES[policy]
        ax.plot(x_val,y_val,ls=line_style,label=name)
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.xlabel("Simulation Period")
    plt.ylabel("Average Total Income")
    plt.savefig(filename,format="png")
    plt.close(fig)
    return
def plotAccumulativeHotelIncome(df,filename,day_idx):
    pathfile = "/".join(filename.split("/")[:-1])
    os.makedirs(pathfile, exist_ok=True)
    x_val = df.columns[day_idx:].tolist()
    px = 1 / plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(2560 * px, 997 * px))
    for index, row in df.iterrows():
        y_val = [row[d] for d in x_val]
        policy = row["Pricing Policy"]
        line_style = LINES[policy]
        ax.plot(x_val, y_val, ls=line_style, label=policy)
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.xlabel("Simulation Period")
    plt.ylabel("Average Total Income")
    plt.savefig(filename, format="png")
    plt.close(fig)
    return

def plotAccumulativePolicyOccupancy(df,filename,day_idx):
    pathfile = "/".join(filename.split("/")[:-1])
    os.makedirs(pathfile, exist_ok=True)
    x_val = df.columns[day_idx:].tolist()
    px = 1 / plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(2560 * px, 997 * px))
    policies = df["Pricing Policy"].unique().tolist()
    # color_bars = {p:COLORS[p] for p in policies}
    color_bar = []
    y_val = {p: [0 for i in x_val] for p in policies}
    for index, row in df.iterrows():
        values = [row[d] for d in x_val]
        policy = row["Pricing Policy"]
        y_val[policy] = [y_val[policy][i] + values[i] for i in range(len(values))]
        color_bar.append(COLORS[policy])

    plt.xticks(range(len(x_val)),x_val)

    bar_width = 0.2
    shift = -0.5*len(policies)
    for p in policies:
        x = np.arange(len(x_val)) + shift * bar_width
        y = [y for y in y_val[p]]
        ax.bar(x, y, bar_width,align='center', color=COLORS[p], label=p)
        shift += 1

    ax.legend()
    plt.xlabel("Simulation Period")
    plt.ylabel("Occupancy Rate (%)")
    plt.tight_layout()
    plt.savefig(filename,format="png")
    plt.close(fig)
    return
def plotPolicyOccupancy(df,filename,day_idx):
    pathfile = "/".join(filename.split("/")[:-1])
    os.makedirs(pathfile, exist_ok=True)
    x_val = df.columns[day_idx:].tolist()
    px = 1 / plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(2560 * px, 997 * px))
    policies = df["Pricing Policy"].unique().tolist()
    # color_bars = {p:COLORS[p] for p in policies}
    color_bar = []
    y_val = {p:[0 for i in x_val] for p in policies}
    normalizer={p:0 for p in policies}
    for index, row in df.iterrows():
        values = [row[d] for d in x_val]
        policy = row["Pricing Policy"]
        y_val[policy] = [y_val[policy][i] + values[i] for i in range(len(values))]
        normalizer[policy] += int(row["Total Number of Rooms"])
        color_bar.append(COLORS[policy])

    plt.xticks(range(len(x_val)),x_val)

    bar_width = 0.2
    shift = -0.5*len(policies)
    for p in policies:
        x = np.arange(len(x_val)) + shift * bar_width
        y = [y/normalizer[p] for y in y_val[p]]
        ax.bar(x, y, bar_width,align='center', color=COLORS[p], label=p)
        shift += 1

    ax.legend()
    plt.xlabel("Simulation Period")
    plt.ylabel("Occupancy Rate (%)")
    plt.tight_layout()
    plt.savefig(filename,format="png")
    plt.close(fig)
    return

def plotUserService(data,filename,text=True):
    budget_policies = list(data.keys())
    pricing_policies = list(data[budget_policies[0]].keys())

    px = 1 / plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(2560 * px, 997 * px))

    plt.xlabel('User\'s Budget')
    plt.ylabel('Average Service')
    #
    plt.xticks(range(len(budget_policies)),
               [f"{b} (<={CONSTANTS.USER_PROFILES.BUDGETS[b]})" for b in budget_policies]
               )
    bar = {}
    bar_width = 0.2
    shift = -.5
    for pp in pricing_policies:
        # if pp in ["+40%", "+60%", "+100%"]:
        #     continue
        y = [
            data[b][pp] for b in budget_policies
        ]
        x = np.arange(len(y)) + shift * bar_width
        bar[pp] = plt.bar(x, y, bar_width, align='center', color=COLORS[pp], label=f"{pp}")
        if text:
            texts = [data[b][pp] * 100 for b in budget_policies]
            texts = [f"{t:.2f}%" for t in texts]
            __addtextlabels(x, y, texts)

        shift += 1

    plt.legend()
    plt.tight_layout()
    plt.savefig(filename,format="png")
    plt.close(fig)
    return

def plotWinningScores(data,filename):
    px = 1 / plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(2560 * px, 997 * px))
    plt.ylabel('Winning Score')
    plt.xlabel('Pricing Policy')
    x_val = list(data.keys())
    y_val = list(data.values())
    colors = [COLORS[p] for p in data]
    ax.bar(x_val,y_val,.1,color=colors)

    # plt.legend()
    plt.tight_layout()
    plt.savefig(filename, format="png")
    plt.close(fig)
    return



def __addtextlabels(x,y,t):
    for i in range(len(x)):
        plt.text(x[i], y[i], t[i], ha = 'center')

#############################################################################################
#############################################################################################
#############################################################################################
'''
    BELOW: OLD CODE 
'''
#############################################################################################
#############################################################################################
#############################################################################################
def printGraph(df,x_axis,y_axis,identifier,folder,filename,day_idx=3):
    os.makedirs(folder, exist_ok=True)
    x_val = df.columns[day_idx:].tolist()
    px = 1/plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(2560*px, 997*px))
    for index,row in df.iterrows():
        name = "_".join([row[i] for i in x_axis])
        y_val = [row[d] for d in x_val]
        policy = row[identifier]
        line_style = LINES[policy]
        ax.plot(x_val,y_val,ls=line_style,label=name)
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    plt.savefig(f"{folder}/{filename}.png",format="png")
    # plt.show()
    plt.close(fig)

def __addlabels(x,y,t):
    for i in range(len(x)):
        plt.text(i, y[i], t[i], ha = 'center')

def printBarGraph(df,x_axis,y_axis,identifier,folder,filename,day_idx=3):
    os.makedirs(folder, exist_ok=True)
    SHADE = {
        "#cc0c0c" : "#c75454",
        "#1ea300" : "#6ead5f",
        "#ff00bf" : "#ff66d9",
        "#6600ff" : "#944dff",
        "#ff00bf" : "#ff66d9",
        "#ff00bf" : "#ff66d9",
    }
    df = df.sort_values("Hotel Id")
    y_val1 = []
    y_val2 = []
    y_val3 = []
    color_bars = []
    color_bars2 = []
    d_range = df.columns[day_idx:].tolist()
    labels = []
    for index,row in df.iterrows():
        y_avg = sum([row[d] for d in d_range])/len(d_range)
        policy = row[identifier]
        color_bars.append(COLORS[policy])
        # if policy not in labels:
        labels.append(policy)
        y_val1.append(y_avg)
        y_tot = int(row["Total Number of Rooms"])
        y_val2.append(y_tot)
        color_bars2.append(SHADE[COLORS[policy]])
        y = y_tot*y_avg
        y_val3.append(y)
    px = 1/plt.rcParams['figure.dpi']
    fig, ax = plt.subplots(figsize=(2560*px, 997*px))
    x_val = df[x_axis[0]].unique().tolist()
    ax.bar(x_val,y_val1, color=color_bars)
    __addlabels(x_val,y_val1,labels)
    plt.rcParams["figure.figsize"] = [21, 9]
    plt.rcParams["figure.autolayout"] = True
    plt.savefig(f"{folder}/{filename}_prc.png",format="png")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(2560*px, 997*px))
    ax.bar(x_val, y_val2, color=color_bars2)
    ax.bar(x_val, y_val3, color=color_bars)
    __addlabels(x_val,y_val2,labels)
    plt.rcParams["figure.figsize"] = [21, 9]
    plt.rcParams["figure.autolayout"] = True
    plt.savefig(f"{folder}/{filename}.png", format="png")
    plt.close(fig)
