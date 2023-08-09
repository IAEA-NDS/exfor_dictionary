import os
import re
import pandas as pd
import requests

from .config import PICKLE_PATH
from .geo.key import API_KEY, GEOCODING_API
from .exfor_dictionary import Diction



def isCountry(code):
    if code[1:4].strip() == code[4:7].strip():
        # print (code[1:4], code[4:7], code[1:4] == code[4:7])
        return True



def get_country_info():
    d = Diction("3")
    country_info = []
    # i = 0

    ## get all countries info in the first iteration
    for key, value in d.get_diction().items():
        print(key, value)
        
        if isCountry(key): # and i < 5:
            # i += 1
            country_code = key[0:4].strip()
            country_name = value["description"]
            obsolete_flag = value["active"]

            ## call geocoding
            if obsolete_flag:

                try:
                    country_fa, country_lat, country_lng, _ = call_geocoding( country_name )

                except:
                    country_fa, country_lat, country_lng, _ = "", "", "", ""

            else:
                country_fa, country_lat, country_lng, _ = "", "", "", ""


            country_info += [
                [
                    country_code,
                    country_name,
                    country_fa,
                    country_lat,
                    country_lng,
                    obsolete_flag,
                ]
            ]
        

    country_df = pd.DataFrame(
        data=country_info,
        columns=[
            "country_code",
            "country_name",
            "country_fa",
            "country_lat",
            "country_lng",
            "obsolete_flag",
        ],
    )
    pd.set_option('display.max_rows', None)
    print(country_df)

    return country_df



def get_institute_info():
    d = Diction("3")

    country_df = pd.read_pickle(  os.path.join(PICKLE_PATH, "country.pickle") )
    
    code = []
    name = []
    flag = []
    formatted_address = []
    addres_country = []
    lat = []
    lng = []

    ## get all institute info
    for key, value in d.get_diction().items():
        try:
            country =  country_df.loc[country_df["country_code"] == key[0:4]]["country_name"].values[0]
            
        except:
            country = ""

        code += [ key ]
        name += [ value["description"] ]
        flag += [ value["active"] ]

        ## call geocoding
        try:
            fa, lt, lg, ctry = call_geocoding( value["description"] + ", " + country )

        except:
            fa, lt, lg, ctry = "", "", "", ""

        formatted_address += [ fa ]  # error due to comma included in the address
        lat += [ lt ]
        lng += [ lg ]
        addres_country += [ ctry ]



    df = pd.DataFrame(
        data={
            "code": code,
            "name": name,
            "formatted_address": formatted_address,
            "addres_country": addres_country,
            "lat": lat,
            "lng": lng,
            "flag": flag,
        },
        columns=[
            "code",
            "name",
            "formatted_address",
            "addres_country",
            "lat",
            "lng",
            "flag",
        ],
    )
    print(df)
    return df


def read_dict3_from_trans():
    ## not used
    dict_file = open(os.path.join("../dictionary/original/diction3.dat"), "r")
    country_info = []
    inst_info = []

    code = []
    name = []
    flag = []
    formatted_address = []
    addres_country = []
    lat = []
    lng = []

    for line in dict_file:
        # print(line[0:8])
        if line[0].isdigit():
            if isCountry(line[0:8]):
                country_code = line[0:4].strip()
                country_name = re.sub("\(|\)", "", line[11:66]).strip()
                obsolete_flag = line[79:80]

                ## call geocoding
                try:
                    country_fa, country_lat, country_lng, _ = call_geocoding(country_name)

                except:
                    country_fa, country_lat, country_lng, _ = "", "", "", ""

                country_info += [
                    [
                        country_code,
                        country_name,
                        country_fa,
                        country_lat,
                        country_lng,
                        obsolete_flag,
                    ]
                ]

            else:
                # if line.startswith('4BLRIJE'):
                code += [line[0:8].strip()]
                n = re.sub("\(|\)", "", line[11:66]).strip()
                name += [n]
                flag += [line[79:80]]

                ## call geocoding
                try:
                    # fa, lt, lg, ctry = call_geocoding(n)
                    fa, lt, lg = '','',''
                except:
                    fa, lt, lg, ctry = "", "", "", ""

                formatted_address += [fa]  # error due to comma included in the address
                lat += [lt]
                lng += [lg]
                addres_country += [ctry]

                # inst_info += [[code, name, formatted_address, lat, lng, flag]]

    dict_file.close()

    country_df = pd.DataFrame(
        data=country_info,
        columns=[
            "country_code",
            "country_name",
            "country_fa",
            "country_lat",
            "country_lng",
            "obsolete_flag",
        ],
    )

    df = pd.DataFrame(
        data={
            "code": code,
            "name": name,
            "formatted_address": formatted_address,
            "addres_country": addres_country,
            "lat": lat,
            "lng": lng,
            "flag": flag,
        },
        columns=[
            "code",
            "name",
            "formatted_address",
            "addres_country",
            "lat",
            "lng",
            "flag",
        ],
    )

    return country_df, df


def call_geocoding(n):
    # example call: https://maps.googleapis.com/maps/api/geocode/json?address=Univ. of Alberta, Edmonton, Alberta, USA&key=API_KEY
    call = "".join([GEOCODING_API, n, "&key=", API_KEY])

    response = requests.get(call)
    g = response.json()
    # print(json.dumps(g, indent =1))

    formatted_address = g["results"][0]["formatted_address"]
    ctry = formatted_address.split(",")[-1]
    lat = g["results"][0]["geometry"]["location"]["lat"]
    lng = g["results"][0]["geometry"]["location"]["lng"]

    print(formatted_address, lat, lng, ctry)

    return formatted_address, lat, lng, ctry


if __name__ == "__main__":
    # country_df = get_country_info()
    # country_df.to_pickle( os.path.join(PICKLE_PATH, "country.pickle") )

    # df = get_institute_info()
    # df.to_pickle( os.path.join(PICKLE_PATH, "institute.pickle") )
    pass
