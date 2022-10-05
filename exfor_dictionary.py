####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Disclaimer: The code is still under developments and not ready
#             to use. It has been made public to share the progress
#             among collaborators.
# Contact:    nds.contact-point@iaea.org
#
####################################################################


import requests
from bs4 import BeautifulSoup
import glob
import re
import os
import json
import pandas as pd
import logging
logging.basicConfig(filename="process.log", level=logging.DEBUG, filemode="w")

from config import DICTIONARY_PATH, DICTIONARY_URL
from abbreviations import abbreviations



def call_diction(diction_num):
    file = diction_json_file(diction_num)
    with open(file) as json_file:
        return json.load(json_file)



def skip_unused_lines(d):
    if "==" in d:
        return True
    elif d[:11] == " " * 11 and d[11].isalpha():
        return True
    else:
        return False



def get_local_trans_num():
    local_dict_files = glob.glob(os.path.join(DICTIONARY_PATH, "trans_backup", "trans.*"))
    # check local dictionary files
    x = []
    for d in local_dict_files:
        x += [re.split(r"\.", os.path.basename(d))[1]]
    if x:
        return max(x)
    else:
        return "10"



def get_server_trans_num():
    x = ["9000"]
    r = requests.get(DICTIONARY_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a", attrs={"href": re.compile(r".*trans.*")})
    for link in links:
        x += [link.get("href").split(".")[-1]]
    return x



def get_latest_trans_num():
    x = get_server_trans_num()
    return max(x)




def download_trans(transnum):
    url = "".join([DICTIONARY_URL, "trans.", str(transnum)])
    print(url)
    r = requests.get(url, allow_redirects=True)

    if r.status_code == 404:
        print("Something wrong with retrieving new dictionary from the IAEA-NDS.")
        logging.error(f"Something wrong with retrieving new dictionary from the IAEA-NDS.")

    else:
        file = dict_filename(transnum)
        open(file, "wb").write(r.content)
        logging.info(f"Download trans.{transnum}")



def download_all_trans():
    x = get_server_trans_num()
    for xx in x:
        download_trans(xx)



def download_latest_dict():
    # get the latest dictionary from https://nds.iaea.org/nrdc/ndsx4/trans/dicts/
    # filename must be in sequence e.g. trans.9124
    local_max = get_local_trans_num()
    latest = get_latest_trans_num()

    if local_max == latest:
        print("Local dictionary is the latest version.")
        pass

    elif local_max > latest:
        print("Something wrong with dictionary file.")

    else:
        download_trans(latest)

    return latest




def dict_filename(latest):
    return os.path.join(DICTIONARY_PATH, "trans_backup", "trans." + str(latest))




def diction_json_file(diction_num: str):
    if diction_num == "950":
        return os.path.join(DICTIONARY_PATH, "json", "Diction-" + str(diction_num) + ".json")
    else:
        j = open("json/Diction-950.json")
        diction_def = json.load(j)
        desc = diction_def[diction_num]["description"]
        return os.path.join(DICTIONARY_PATH, "json", "Diction-" + str(diction_num) + "-" + desc + ".json")




def write_diction_json(diction_num: str, diction_dict):
    file = diction_json_file(diction_num)
    with open(file, "w") as json_file:
        json.dump(diction_dict, json_file, indent=2)




def get_diction_difinition(latest) -> dict:
    """
    read and store diction number and description from diction 950
    """
    file = dict_filename(latest)
    with open(file) as f:
        lines = f.readlines()
    dict = {}

    diction_950 = False

    for line in lines:
        if line.startswith("DICTION"):
            diction_num = re.split("\s{2,}", line)[1]
            if int(diction_num) == 950:
                diction_950 = True
                continue

        elif line.startswith("ENDDICTION") and diction_950:
            diction_950 = False
            break

        elif diction_950:

            param = str(line[:11].rstrip().lstrip())
            desc = line[11:66].rstrip()
            flag = line[79:80]
            dict2 = {
                "diction_num": param,
                "description": desc,
                "active": False if flag == "O" else True,
            }

            dict[param] = {
                "description": desc,
                "active": False if flag == "O" else True,
            }

    write_diction_json("950", dict)
    # print(json.dumps(dict, indent=1))
    return dict



def parse_dictionary(latest):

    ## start parsing all dictions
    file = dict_filename(latest)
    with open(file) as f:
        lines = f.readlines()

        new = False
        for line in lines:
            if line.startswith("DICTION"):
                diction = []
                new = True
                diction_num = re.split("\s{2,}", line)[1]
                fname = os.path.join(
                    DICTIONARY_PATH, "diction", "diction" + str(diction_num) + ".dat"
                )
                o = open(fname, "w")
                # o.write("# " + line[:66] + "\n")
                o.write(line)
                continue

            elif line.startswith("ENDDICTION") and diction_num != "950":
                new = False
                o.close()
                continue

            elif new:
                # o.write(line[:66] + "\n")
                o.write(line)
                diction += [line]




def conv_dictionary_tojson(latest) -> dict:
    ## From diction 950, get definitions of each diction
    diction_def = get_diction_difinition(latest)

    for diction_num in diction_def:
        print(diction_num)

        fname = os.path.join(
            DICTIONARY_PATH, "diction", "diction" + str(diction_num) + ".dat"
        )

        with open(fname) as f:
            diction = f.read().splitlines()[1:]
        # print(diction)
        diction_dict = {}

        institute_df = pd.read_pickle("pickles/institute.pickle")
        institute_df["code"] = institute_df["code"].str.rstrip()
        institute_df = institute_df.set_index("code")
        institute_dict = institute_df.to_dict(orient="index")

        country_df = pd.read_pickle("geo/country.pickle")
        country_df = country_df.set_index("country_code")
        country_dict = country_df.to_dict(orient="index")

        parames = {}
        
        if int(diction_num) in [
            209,
            207,
            33,
            23,
            22,
            21,
            20,
            19,
            18,
            17,
            16,
            15,
            8,
            7,
            5,
            4,
            3,
            2,
        ]:
            for d in diction:
                print(d)
                if skip_unused_lines(d):
                    continue

                if not d.startswith(" "):
                    from abbreviations import institute_abbr

                    param = d[:11].rstrip()
                    regex = r"\((.*)\)"
                    desc = re.match(regex, d[11:66]).group(1)
                    desc = abbreviations(institute_abbr, desc)
                    flag = d[79:80]

                    if int(diction_num) == 3:
                        ### for DICTION 3: Institute
                        if not param[1:4].rstrip() == param[4:7]:

                            if institute_dict.get(param):
                                addr = institute_dict[param]["formatted_address"]
                                lat = institute_dict[param]["lat"]
                                lng = institute_dict[param]["lng"]
                            else:
                                addr = lat = lng = None

                        elif param[1:4].rstrip() == param[4:7]:
                            lat = country_dict[param[0:4].rstrip()]["country_lat"]
                            lng = country_dict[param[0:4].rstrip()]["country_lng"]

                        else:
                            lat = lng = None

                        parames[param] = {
                            "x4code": param,
                            "description": desc,
                            "latitude": lat,
                            "longitude": lng,
                            "address": addr,
                            "active": False if flag == "O" else True,
                        }

                    if int(diction_num) == 5:
                        ### for DICTION   5  Journals
                        journal_contry = d[62:66]

                        if country_dict.get(journal_contry):

                            parames[param] = {
                                "x4code": param,
                                "description": desc,
                                "pulished_country": journal_contry,
                                "pulished_country_name": country_dict[journal_contry][
                                    "country_name"
                                ],
                                "active": False if flag == "O" else True,
                            }

                    else:
                        parames[param] = {
                            "x4code": param,
                            "description": desc,
                            "active": False if flag == "O" else True,
                        }

                    diction_dict = {
                        "diction_num": diction_num,
                        "diction_def": diction_def[str(diction_num)]["description"],
                        "children": parames,
                    }

        elif int(diction_num) in [144, 43, 38, 35, 34, 32, 31, 30, 6, 1]:
            for d in diction:
                skip_unused_lines(d)
                if not d.startswith(" "):
                    param = d[:11].rstrip()
                    desc = d[11:66].rstrip()
                    flag = d[79:80]

                    if int(diction_num) == 6:
                        ### for the DICTION   5  Reports
                        report_inst = d[59:66]
                        if institute_dict.get(report_inst):
                            parames[param] = {
                                "x4code": param,
                                "description": desc[:-7].rstrip(),
                                "publisher": report_inst,
                                "publisher_name": institute_dict[report_inst]["name"],
                                "active": False if flag == "O" else True,
                            }

                    else:
                        parames[param] = {
                            "x4code": param,
                            "description": desc,
                            "active": False if flag == "O" else True,
                        }

                diction_dict = {
                    "diction_num": diction_num,
                    "diction_def": diction_def[str(diction_num)]["description"],
                    "children": parames,
                }

        elif int(diction_num) == 24:
            ### DICTION 24: Data headings
            from abbreviations import head_unit_abbr

            desc = []
            for d in diction[11:]:
                param = ""
                flag = ""
                desc = ""
                param2 = ""
                if d[0].isalpha() or d[0].isdigit():
                    flag = d[79:80]  # obsolute or not
                    param = d[:11].rstrip()
                    desc = d[11:65].rstrip()
                    param2 = d[65:66].rstrip()

                    if param.startswith("DATA") and not "ERR" in param:
                        param2 = "DATA"
                    elif param.startswith("DATA") and "ERR" in param:
                        param2 = "DATA_E"

                elif d.startswith(" " * 11):
                    continue

                if param:
                    desc = abbreviations(head_unit_abbr, "".join(desc))
                    parames[param] = {
                        "x4code": param,
                        "description": desc,
                        "param2": param2,
                        "active": False if flag == "O" else True,
                    }

            diction_dict = {
                "diction_num": diction_num,
                "diction_def": diction_def[str(diction_num)]["description"],
                "children": parames,
            }

        elif int(diction_num) == 25:
            ### DICTION 25: Data units
            from abbreviations import head_unit_abbr

            desc = []
            for d in diction[1:]:
                if d[0].isalpha() or d[0].isdigit():
                    flag = d[79:80]  # obsolute or not
                    param = d[:11].rstrip()
                    desc = d[11:44].rstrip()
                    param2 = d[44:55].rstrip()
                    factor = d[55:66].strip()

                elif d.startswith(" " * 11):
                    continue

                if param:
                    desc = abbreviations(head_unit_abbr, "".join(desc))
                    parames[param] = {
                        "x4code": param,
                        "description": desc,
                        "param2": param2,
                        "unit conversion factor": factor,
                        "active": False if flag == "O" else True,
                    }

                diction_dict = {
                    "diction_num": diction_num,
                    "diction_def": diction_def[str(diction_num)]["description"],
                    "children": parames,
                }
                desc = []

        elif int(diction_num) == 144:
            ### DICTION 25: Data units
            from abbreviations import head_unit_abbr

            desc = []
            for d in diction[1:]:
                if d[0].isalpha() or d[0].isdigit():
                    flag = d[79:80]  # obsolute or not
                    param = d[:15].rstrip()
                    desc = d[15:66].rstrip()

                elif d.startswith(" " * 11):
                    continue

                if param:
                    desc = abbreviations(head_unit_abbr, "".join(desc))
                    parames[param] = {
                        "x4code": param,
                        "description": desc,
                        "active": False if flag == "O" else True,
                    }

                diction_dict = {
                    "diction_num": diction_num,
                    "diction_def": diction_def[str(diction_num)]["description"],
                    "children": parames,
                }
                desc = []

        elif int(diction_num) == 213:
            ### DICTION 25: Data units
            from abbreviations import head_unit_abbr

            desc = []
            for d in diction[1:]:
                if d[0].isalpha() or d[0].isdigit():
                    flag = d[79:80]  # obsolute or not
                    param = d[:11].rstrip()
                    param2 = d[11:16].rstrip()
                    param3 = d[16:20].rstrip()
                    desc = d[20:66].rstrip()

                elif d.startswith(" " * 11):
                    continue

                if param:
                    desc = abbreviations(head_unit_abbr, "".join(desc))
                    parames[param] = {
                        "x4code": param,
                        "description": desc,
                        "param2": param2,
                        "param3": param3,
                        "active": False if flag == "O" else True,
                    }

                diction_dict = {
                    "diction_num": diction_num,
                    "diction_def": diction_def[str(diction_num)]["description"],
                    "children": parames,
                }
                desc = []

        elif int(diction_num) == 236:
            """
            reaction string
            exception for TRS,POL/DA/DA/DE,*/*/*+*,ANA, and
            multiline of description are not implemented yet.
            """
            from abbreviations import reaction_abbr

            cont = False
            desc = []
            for d in diction[27:]:
                if skip_unused_lines(d):
                    continue

                if (
                    d[0].isalpha()
                    or d[0].isdigit()
                    or any(d.startswith(s) for s in [",", "("])
                    or not cont
                ):
                    cont = False
                    flag = d[79:80]  # obsolute flag

                    ### get EXFOR code
                    if d[17] == " " and d[18].isalpha():
                        ## for the case of reaction code with the second parameter flag
                        param = d[:17].rstrip()
                        param2 = d[18:22].rstrip()

                    elif " " not in d[:22] and d[22] != "(":
                        ## for the case of long reaction code
                        param = d[:30].rstrip()
                        cont = True
                    else:
                        param = d[:22].rstrip()
                        param2 = ""

                    ## get description
                    if d[22] == "(":
                        desc = d[22:66].rstrip()
                        if not desc[0].endswith(")"):
                            cont = True
                            continue

                elif cont and d.startswith(" " * 22):
                    desc += d[22:66].rstrip()
                    if not desc[-1].endswith(")"):
                        cont = True
                    elif desc[-1].endswith(")"):
                        cont = False

                else:
                    cont = False
                    desc = []
                    continue

                if not cont and param:
                    desc = abbreviations(reaction_abbr, "".join(desc))
                    parames[param] = {
                        "x4code": param,
                        "description": desc,
                        "param2": param2,
                        "active": False if flag == "O" else True,
                    }

                    diction_dict = {
                        "diction_num": diction_num,
                        "diction_def": diction_def[str(diction_num)]["description"],
                        "children": parames,
                    }
                    desc = []

        else:
            """
            Skip other unnecessary dictionaries: 43,45,47,48,52,37,35,16,213,227,235
            """
            pass

        ## save as JSON
        if diction_dict:
            write_diction_json(diction_num, diction_dict)



class Diction:
    def __init__(self):
        self.diction_num = None

        # self.incident_en_heads =self.get_incident_en_heads()



    def read_diction(self, diction_num):
        if diction_num:
            file = diction_json_file(diction_num)
            with open(file) as json_file:
                return json.load(json_file)["parameters"]




    def get_incident_en_heads(self):
        ## diction 24: Data heads, get_x
        diction = self.read_diction("24")
        return [
            h
            for h in diction.keys()
            if diction[h]["param2"] == "A"
            and diction[h]["active"]
            and "-DN" not in h
            and "-NM" not in h
        ]



    def get_incident_en_err_heads(self):
        ## diction 24: Data heads, get_dx
        diction = self.read_diction("24")
        return [
            h
            for h in diction.keys()
            if diction[h]["param2"] == "B"
            and diction[h]["active"]
            and "-DN" not in h
            and "-NM" not in h
        ]



    def get_data_heads(self):
        ## diction 24: Data heads, for y
        diction = self.read_diction("24")
        return [
            h
            for h in diction.keys()
            if diction[h]["param2"] == "DATA"
            and diction[h]["active"]
            and "-DN" not in h
            and "-NM" not in h
        ]



    def get_data_err_heads(self):
        ## diction 24: Data heads, for d_y
        diction = self.read_diction("24")
        return [
            h
            for h in diction.keys()
            if diction[h]["param2"] == "DATA_E"
            and diction[h]["active"]
            and "-DN" not in h
            and "-NM" not in h
        ]



    def get_outgoing_e_heads(self):
        ## diction 24: Data heads, measured energy
        diction = self.read_diction("24")
        return [
            h
            for h in diction.keys()
            if diction[h]["param2"] == "E" and diction[h]["active"]
        ]


    def get_level_heads(self):
        ## diction 24: Data heads, measured level
        diction = self.read_diction("24")
        return [
            h
            for h in diction.keys()
            if diction[h]["param2"] == "L" and diction[h]["active"]
        ]



    def get_level_angle(self):
        ## diction 24: Data heads, measured level
        diction = self.read_diction("24")
        return [
            h
            for h in diction.keys()
            if diction[h]["param2"] == "G" and diction[h]["active"]
        ]



    def get_mass_heads(self):
        ## diction 24: Data heads, get_x
        diction = self.read_diction("24")
        return [
            h
            for h in diction.keys()
            if diction[h]["param2"] == "J" and diction[h]["active"]
        ]



    def get_elem_heads(self):
        ## diction 24: Data heads, get_x
        diction = self.read_diction("24")
        return [
            h
            for h in diction.keys()
            if diction[h]["param2"] == "I" and diction[h]["active"]
        ]



    def get_unit_factor(self, datahead):
        ## diction 25: Data units
        diction_num = "25"
        diction = self.read_diction(diction_num)
        factor = diction[datahead][
            "unit conversion factor"
        ]  # if diction[datahead]["active"]
        if factor == "":
            return 1.0
        else:
            return factor



    def get_details(self, diction_num, key):
        diction = self.read_diction(diction_num)
        if diction.get(key):
            return diction[key]["description"]
        else:
            return key




if __name__ == "__main__":


    latest = get_latest_trans_num()
    download_trans(latest)
    parse_dictionary(latest)
    conv_dictionary_tojson(latest)





