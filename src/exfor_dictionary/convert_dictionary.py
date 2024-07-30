####################################################################
#
# This file is a part of exfor-parser/dataexplorer.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Disclaimer: The code is still under developments and not ready
#             to use. It has been made public to share the progress
#             among collaborators.
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import glob
import re
import os
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup

from exfor_dictionary.default_config import DICTIONARY_PATH, DICTIONARY_URL, PICKLE_PATH
from exfor_dictionary.abbreviations import convert_abbreviations, institute_abbr, head_unit_abbr, reaction_abbr

session = requests.Session()
if 'OPENAREA_USER' in os.environ and 'OPENAREA_PWD' in os.environ:
    session.auth = (os.environ['OPENAREA_USER'], os.environ['OPENAREA_PWD'])
else:
    print('No OPENAREA credentials ("OPENAREA_USER", "OPENAREA_PWD") provided as environment variables. Accessing Open Area without authentification. ')

def get_local_trans_nums():
    local_dict_files = glob.glob(
        os.path.join(DICTIONARY_PATH, "trans_backup", "trans.*")
    )
    x = ["9090"]
    for d in local_dict_files:
        x += [re.split(r"\.", os.path.basename(d))[1]]

    return x


def get_server_trans_nums():
    x = ["9000"]

    r = session.get(DICTIONARY_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a", attrs={"href": re.compile(r".*trans.*")})
    for link in links:
        x += [link.get("href").split(".")[-1]]

    # trans_nums should be unique
    x = set(x)

    print(x)
    # remove obstruction
    for incompatible_trans_num in ["9927", "9928"]:
        if incompatible_trans_num in x:
            x.remove(incompatible_trans_num)

    return x


def get_latest_trans_num(x):
    return max(x)


def download_trans(transnum):
    url = "".join([DICTIONARY_URL, "trans.", str(transnum)])
    print(url)
    r = session.get(url, allow_redirects=True)

    if r.status_code == 404:
        print("Something wrong with retrieving new dictionary from the IAEA-NDS.")

    else:
        file = dict_filename(transnum)
        open(file, "wb").write(r.content)


def download_all_trans():
    x = get_server_trans_nums()
    for xx in x:
        download_trans(xx)


def download_latest_dict():
    # get latest dictionary from https://nds.iaea.org/nrdc/ndsx4/trans/dictionaries/
    # filename must be in sequence e.g. trans.9123, trans.9124..
    local_max = get_latest_trans_num(get_local_trans_nums())
    remote_max = get_latest_trans_num(get_server_trans_nums())

    if local_max == remote_max:
        print("Local dictionary is the latest version.")
        return local_max

    elif local_max > remote_max:
        print("Something wrong with dictionary file.")
        exit()

    else:
        download_trans(remote_max)
        return remote_max


def dict_filename(latest):
    trans_folder = os.path.join(DICTIONARY_PATH, "trans_backup")
    # ensure folder exists
    os.makedirs(trans_folder, exist_ok=True)

    return os.path.join( trans_folder, "trans." + str(latest))


def diction_json_file(diction_num: str):
    return os.path.join(
        DICTIONARY_PATH, "trans_json", "dictions", "Diction-" + str(diction_num) + ".json"
    )


def write_diction_json(diction_num: str, diction_dict):
    file = diction_json_file(diction_num)
    with open(file, "w") as json_file:
        json.dump(diction_dict, json_file, indent=2)


def write_trans_json_file(trans_num: str, exfor_dictionary):
    file = os.path.join(DICTIONARY_PATH, "trans_json", "trans." + str(trans_num) + ".json")
    latest = os.path.join(DICTIONARY_PATH, "latest.json")
    with open(file, "w") as json_file:
        json.dump(exfor_dictionary, json_file, indent=2)
    with open(latest, "w") as json_file:
        json.dump(exfor_dictionary, json_file, indent=2)


def get_diction_definition(latest) -> dict:
    """
    read and store diction number and description from diction 950
    """

    pattern = r"^SUBDICT *90001950.*$\r?\n(?P<dict950>(?s:.)*)\r?\n^ENDSUBDICT"

    file = dict_filename(latest)
    with open(file) as f:
        lines = f.read()

    result = {}

    match = re.search(pattern, lines, flags = re.MULTILINE)
    if not match:
        raise ValueError(f'Could not find metadict 950 in latest trans files: {latest}')
    
    dict950 = match.groupdict()['dict950']

    for line in dict950.splitlines():

        x4code = str(line[:11].strip())
        desc = line[11:66].strip()
        flag = line[79:80]

        result[x4code] = {
            "description": desc,
            "active": False if flag == "O" else True,
        }

    write_diction_json("950", result)

    return result


def parse_dictionary(latest):

    pattern = r"^SUBDICT *\d{5}(?P<dict_id>\d{3}).*$(?P<exfor_dict>(?s:.)*?)^ENDSUBDICT"

    file = dict_filename(latest)
    with open(file) as f:
        lines = f.read()

    output_folder = os.path.join(DICTIONARY_PATH, "trans_backup", "dictions")
    # ensure folder exists
    os.makedirs(output_folder,exist_ok=True)

    filename = dict_filename(latest)

    with open(filename) as f:
        lines = f.read()

    for match in re.finditer(pattern, lines, re.MULTILINE):
        diction_num = match.groupdict()['dict_id'].lstrip('0')
        dict_lines = match.group()

        fname = os.path.join(output_folder, "diction" + str(diction_num) + ".dat")
        with open(fname, "w") as filehandle:
            filehandle.write(dict_lines)
            

def is_comment_line(d):
    if "==" in d:
        return True
    elif d[:11] == " " * 11 and d[11].isalpha():
        return True
    else:
        return False


def conv_dictionary_to_json(latest) -> dict:
    ## load pickles for additional info
    """
    Note: these pickle are included in the main EXFOR parser reporsitory
    """

    institute_df = pd.read_pickle(os.path.join(PICKLE_PATH, "institute.pickle"))
    institute_df["code"] = institute_df["code"].str.strip()
    institute_df = institute_df.set_index("code")
    institute_dict = institute_df.to_dict(orient="index")

    country_df = pd.read_pickle(os.path.join(PICKLE_PATH, "country.pickle"))
    country_df = country_df.set_index("country_code")
    country_dict = country_df.to_dict(orient="index")


    ## Get definitions of each DICTION from DICTION 950
    dictions = get_diction_definition(latest)

    ## initialize dict
    exfor_dictionary = {}
    exfor_dictionary["definitions"] = dictions
    exfor_dictionary["dictionaries"] = {}

    for diction_num in dictions:
        folder = os.path.join(DICTIONARY_PATH, "trans_backup", "dictions")
        fname = os.path.join(folder, "diction" + str(diction_num) + ".dat")

        with open(fname) as f:
            diction = f.read().splitlines()[1:-1]

        diction_dict = {}
        codes = {}

        if int(diction_num) in [209, 207, 33, 23, 22, 21, 20, 19, 18,
            17, 16, 15, 8, 7, 5, 4, 3, 2]:
            for line in diction:
                if is_comment_line(line):
                    continue

                if not line.startswith(" "):

                    x4code = line[:11].strip()
                    regex = r"\((.*)\)"
                    desc = re.match(regex, line[11:66]).group(1)
                    desc = convert_abbreviations(institute_abbr, desc)
                    flag = line[79:80]

                    if int(diction_num) == 3:
                        ### for DICTION 3: Institute
                        if not x4code[1:4].strip() == x4code[4:7]:
                            if institute_dict.get(x4code):
                                addr = institute_dict[x4code]["formatted_address"]
                                lat = institute_dict[x4code]["lat"]
                                lng = institute_dict[x4code]["lng"]
                            else:
                                addr = lat = lng = None

                        elif x4code[1:4].strip() == x4code[4:7]:
                            lat = country_dict[x4code[0:4].strip()]["country_lat"]
                            lng = country_dict[x4code[0:4].strip()]["country_lng"]

                        else:
                            lat = lng = None

                        codes[x4code] = {
                            "description": desc,
                            "latitude": lat,
                            "longitude": lng,
                            "address": addr,
                            "active": False if flag == "O" or flag == "X" else True,
                        }

                    if int(diction_num) == 5:
                        ### for DICTION   5  Journals
                        journal_contry = line[62:66]

                        if country_dict.get(journal_contry):
                            codes[x4code] = {
                                "description": desc,
                                "pulished_country_code": journal_contry,
                                "pulished_country_name": country_dict[journal_contry][
                                    "country_name"
                                ],
                                "active": False if flag == "O" or flag == "X" else True,
                            }

                    else:
                        codes[x4code] = {
                            "description": desc,
                            "active": False if flag == "O" or flag == "X" else True,
                        }

        elif int(diction_num) in [144, 43, 38, 35, 34, 32, 31, 30, 6, 1]:
            for line in diction:
                is_comment_line(line)
                if not line.startswith(" "):
                    x4code = line[:11].strip()
                    desc = line[11:66].strip()
                    flag = line[79:80]

                    if int(diction_num) == 6:
                        ### for the DICTION   5  Reports
                        report_inst = line[59:66]
                        if institute_dict.get(report_inst):
                            codes[x4code] = {
                                "description": desc[:-7].strip(),
                                "publisher": report_inst,
                                "publisher_name": institute_dict[report_inst]["name"],
                                "active": False if flag == "O" or flag == "X" else True,
                            }

                    else:
                        codes[x4code] = {
                            "description": desc,
                            "active": False if flag == "O" or flag == "X" else True,
                        }

        elif int(diction_num) == 24:
            ### DICTION 24: Data headings

            desc = []
            for line in diction[11:]:
                x4code = ""
                flag = ""
                desc = ""
                additional_code = ""
                if line[0].isalpha() or line[0].isdigit():
                    flag = line[79:80]  # obsolete flag
                    x4code = line[:11].strip()
                    desc = line[11:65].strip()
                    additional_code = line[65:66].strip()

                    if x4code.startswith("DATA") and not "ERR" in x4code:
                        additional_code = "DATA"
                    elif x4code.startswith("DATA") and "ERR" in x4code:
                        additional_code = "DATA_E"
                    elif x4code == "ERR-T":
                        additional_code = "DATA_E"

                elif line.startswith(" " * 11):
                    continue

                if x4code:
                    desc = convert_abbreviations(head_unit_abbr, "".join(desc))
                    codes[x4code] = {
                        "description": desc,
                        "additional_code": additional_code,
                        "active": False if flag == "O" or flag == "X" else True,
                    }

        elif int(diction_num) == 25:
            ### DICTION 25: Data units

            desc = []
            for line in diction[1:]:
                if line[0].isalpha() or line[0].isdigit():
                    flag = line[79:80]  # obsolete flag
                    x4code = line[:11].strip()
                    desc = line[11:44].strip()
                    additional_code = line[44:55].strip()
                    factor = line[55:66].strip()

                elif line.startswith(" " * 11):
                    continue

                if x4code:
                    desc = convert_abbreviations(head_unit_abbr, "".join(desc))
                    codes[x4code] = {
                        "description": desc,
                        "additional_code": additional_code,
                        "unit_conversion_factor": factor,
                        "active": False if flag == "O" or flag == "X" else True,
                    }

                desc = []

        elif int(diction_num) == 144:
            ### DICTION 114: Data libraries

            desc = []
            for line in diction[1:]:
                if line[0].isalpha() or line[0].isdigit():
                    flag = line[79:80]  # obsolete flag
                    x4code = line[:15].strip()
                    desc = line[15:66].strip()

                elif line.startswith(" " * 11):
                    continue

                if x4code:
                    desc = convert_abbreviations(head_unit_abbr, "".join(desc))
                    codes[x4code] = {
                        "description": desc,
                        "active": False if flag == "O" or flag == "X" else True,
                    }

                desc = []

        elif int(diction_num) == 213:
            ### DICTION 25: Data units

            desc = []
            for line in diction[1:]:
                if line[0].isalpha() or line[0].isdigit():
                    flag = line[79:80]  # obsolete flag
                    x4code = line[:11].strip()
                    additional_code = line[11:16].strip()
                    x4code3 = line[16:20].strip()
                    desc = line[20:66].strip()

                elif line.startswith(" " * 11):
                    continue

                if x4code:
                    desc = convert_abbreviations(head_unit_abbr, "".join(desc))
                    codes[x4code] = {
                        "description": desc,
                        "additional_code": additional_code,
                        "x4code3": x4code3,
                        "active": False if flag == "O" or flag == "X" else True,
                    }

                desc = []

        elif int(diction_num) == 236:
            """
            reaction string
            exception for TRS,POL/DA/DA/DE,*/*/*+*,ANA, and
            multiline of description are not implemented yet.

            # Case 1
            ,POL/DA,,VAP      NO  (Vector analyzing power, iT(11))            3000023601237
            # Case 2
            ,POL/DA/DA,*/*,ANANO  (Analyzing power d2/dA(*)/dA(*))            3000023601238
            # Case 3
            PR,NU/DA/DE,N+*F/NFYAE(Diff.prompt neut.mult.d/dA(n+frag.spec.    3000023600699
                                )/dE(n))                                    3000023600700
                                (Differential prompt neutron multiplicity   3000023600701
                                with respect to angle between neutron and  3000023600702
                                fission fragment specified and energy of   3000023600703
                                neutron)                                   3000023600704
            # Case 4
            ,POL/DA/DA/DE,*,ANA                                              93000023601239
                            NO  (Analyzing power dA1/dA2/dE f.particle      3000023601240
                                specified)                                 3000023601241
            # Case 5
            ,POL/DA/DA/DE,*/*/*,ANA                                          93000023601244
                            NO  (Analyzing power dA1/dA2/dE1 f.particles    3000023601245
                                spec.)                                     3000023601246
            """

            cont = False
            desc = []
            for line in diction[27:]:
                if is_comment_line(line):
                    continue

                ### get EXFOR code
                if (
                    line[0].isalpha()
                    or line[0].isdigit()
                    or any(line.startswith(s) for s in [",", "("])
                    or not cont
                ):
                    cont = False
                    flag = line[79:80]  # obsolete flag

                    if not line.startswith(" ") and line[22] == "(":
                        ## Case 1, 2, and 3
                        x4code = line[:18].strip()
                        additional_code = line[18:22].strip()

                    elif " " not in line[:18] and line[22] != "(":
                        ## Case 4, 5
                        x4code = line[:30].strip()

                    elif line.startswith(" " * 18) and line[18] != " " and line[22] == "(":
                        ## Case 4, 5
                        additional_code = line[18:22].strip()

                    ## get description
                    if line[22] == "(":
                        desc = line[22:66].strip()
                        cont = True
                        if desc[-1].endswith(")"):
                            cont = False

                elif line.startswith(" " * 22):
                    desc += line[22:66].strip()
                    if not desc[-1].endswith(")"):
                        cont = True
                    elif desc[-1].endswith(")"):
                        cont = False

                else:
                    cont = False
                    desc = []

                if not cont and x4code:
                    desc = convert_abbreviations(reaction_abbr, "".join(desc))
                    codes[x4code] = {
                        "description": desc,
                        "additional_code": additional_code,
                        "active": False if flag == "O" or flag == "X" else True,
                    }

                    desc = []

        else:
            """
            Skip other unnecessary DICTION: 47,48,52,227,235
            """
            continue

        # create dictionary content
        diction_dict = {
            diction_num: {
                "diction_name": dictions[str(diction_num)]["description"],
                "codes": codes,
            }
        }

        if diction_dict:
            # append dictionary content to json/trans.***.json
            exfor_dictionary["dictionaries"].update(diction_dict)

            # create individual diction-json files just in case, will be deleted in the future
            write_diction_json(diction_num, diction_dict)

    write_trans_json_file(latest, exfor_dictionary)

    return exfor_dictionary


def update_dictionary_to_latest():
    ## check the latest number of trans file in remote server and download it
    ## note that the oldest file that this parser can process is trans.9090.
    latest = download_latest_dict()

    ## conversion to json
    parse_dictionary(latest)
    conv_dictionary_to_json(latest)

    print("Latest dictionary trans file is trans." + latest)
    return latest


if __name__ == "__main__":
    update_dictionary_to_latest()

