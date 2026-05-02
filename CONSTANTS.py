class TIME_PERIOD:
    TEN_DAYS = 10
    TWENTY_DAYS = 20
    ONE_WEEK = 7
    TWO_WEEKS = 15
    ONE_MONTH = 30
    TWO_MONTHS = 60
    THREE_MONTH = 90
    ONE_YEAR = 365

class FEATURES:
    TYPE = "Room Type"
    SINGLE = "single"
    DOUBLE = "double"
    TRIPLE = "triple"
    SUITS = "suite"
    BED = "Bed Size"
    QUEEN = "queen"
    KING = "king"
    TWIN = "twin"
    DOUBLE2 = "double double"
    STUDIO = "studio"

    OPTIONS = {
        TYPE: {
            "NUM_OF_OPTIONS" : 4,
            "LIST_OF_OPTIONS" : [SINGLE, DOUBLE, TRIPLE, SUITS]
        },
        BED: {
            "NUM_OF_OPTIONS" : 5,
            "LIST_OF_OPTIONS" : [QUEEN,KING,TWIN,DOUBLE2,STUDIO]
        }

    }

    DEFAULT_LIST_OF_FEATURES = [TYPE]
    DEFAULT_VALUE = {
        TYPE: SINGLE,
        BED: KING
    }
class PRICING_POLICIES:
    FAIRPLAY = "fairplay"
    MCMC = "MCMC-Bayesian"
    BAYESIAN = "Bayesian"
    SEVENTEEN_PRC = "+17%"
    TWENTY_PRC = "+20%"
    FORTY_PRC = "+40%"
    FIFTY_PRC = "+50%"
    SIXTY_PRC = "+60%"
    SEVENTY_PRC = "+70%"
    HUNDRED_PRC = "+100%"
    TWO_HUNDRED_PRC = "+200%"

    INCREMENT= {
        SEVENTEEN_PRC:0.17,
        TWENTY_PRC : 0.2,
        FORTY_PRC : 0.4,
        FIFTY_PRC : 0.5,
        SIXTY_PRC : 0.6,
        SEVENTY_PRC : 0.7,
        HUNDRED_PRC : 1,
        TWO_HUNDRED_PRC : 2,
        FAIRPLAY : 0,
        "all" : "all"
    }
    DEFAULT_POLICIES = [
        FAIRPLAY,
        SEVENTEEN_PRC,
        # TWENTY_PRC,
        FORTY_PRC,
        FIFTY_PRC,
        # SIXTY_PRC
    ]

class USER_PROFILES:
    USER_PROFILES ={
        "VERY LOW": 45,
        "LOW" : 65,
        "MED" : 80,
        "HIGH" : 100,
        "VERY HIGH" : 200,
        "UNLIMITED" :1e+10
    }
    BUDGETS = {
        "VERY LOW": "45\N{euro sign}",
        "LOW": "65\N{euro sign}",
        "MED": "80\N{euro sign}",
        "HIGH": "100\N{euro sign}",
        "VERY HIGH": "200\N{euro sign}",
        "UNLIMITED": "+\u221e"
    }