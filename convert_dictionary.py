
import requests
from bs4 import BeautifulSoup
import glob
import re
import os
import json
import pandas as pd


try:
    from config import DICTIONARY_PATH, DICTIONARY_URL, PICKLE_PATH
    from abbreviations import convert_abbreviations

except:
    import sys

    sys.path.append("../exfor_dictionary/")
    from exfor_dictionary.config import DICTIONARY_PATH, DICTIONARY_URL, PICKLE_PATH
    from exfor_dictionary.abbreviations import convert_abbreviations


def get_local_trans_nums():
    local_dict_files = glob.glob(
        os.path.join(DICTIONARY_PATH, "trans_backup", "trans.*")
    )
    x = []
    for d in local_dict_files:
        x += [re.split(r"\.", os.path.basename(d))[1]]

    return x


def get_server_trans_nums():
    x = ["9000"]
    r = requests.get(DICTIONARY_URL)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a", attrs={"href": re.compile(r".*trans.*")})
    for link in links:
        x += [link.get("href").split(".")[-1]]
        
    # remove obstruction
    x.remove("9927")
    return x


def get_latest_trans_num(x):
    return max(x)


def download_trans(transnum):
    url = "".join([DICTIONARY_URL, "trans.", str(transnum)])
    print(url)
    r = requests.get(url, allow_redirects=True)

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
    return os.path.join(DICTIONARY_PATH, "trans_backup", "trans." + str(latest))


def diction_json_file(diction_num: str):
    return os.path.join(
        DICTIONARY_PATH, "json", "dictions", "Diction-" + str(diction_num) + ".json"
    )

def write_diction_json(diction_num: str, diction_dict):
    file = diction_json_file(diction_num)
    with open(file, "w") as json_file:
        json.dump(diction_dict, json_file, indent=2)


def write_trans_json_file(trans_num: str, exfor_dictionary):
    file = os.path.join(DICTIONARY_PATH, "json", "trans." + str(trans_num) + ".json")
    with open(file, "w") as json_file:
        json.dump(exfor_dictionary, json_file, indent=2)


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
            x4code = str(line[:11].rstrip().lstrip())
            desc = line[11:66].rstrip()
            flag = line[79:80]

            dict[x4code] = {
                "description": desc,
                "active": False if flag == "O" else True,
            }

    write_diction_json("950", dict)

    return dict


def parse_dictionary(latest):
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
                    DICTIONARY_PATH,
                    "trans_backup/dictions",
                    "diction" + str(diction_num) + ".dat",
                )
                o = open(fname, "w")
                o.write(line)
                continue

            elif line.startswith("ENDDICTION") and diction_num != "950":
                new = False
                o.close()
                continue

            elif new:
                o.write(line)
                diction += [line]


def skip_unused_lines(d):
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
    institute_df["code"] = institute_df["code"].str.rstrip()
    institute_df = institute_df.set_index("code")
    institute_dict = institute_df.to_dict(orient="index")

    country_df = pd.read_pickle(os.path.join(PICKLE_PATH, "country.pickle"))
    country_df = country_df.set_index("country_code")
    country_dict = country_df.to_dict(orient="index")

    ## Get definitions of each DICTION from DICTION 950
    dictions = get_diction_difinition(latest)

    ## initialize dict
    exfor_dictionary = {}
    exfor_dictionary["definitions"] = dictions
    exfor_dictionary["dictionaries"] = {}

    for diction_num in dictions:
        fname = os.path.join(
            DICTIONARY_PATH,
            "trans_backup/dictions",
            "diction" + str(diction_num) + ".dat",
        )

        with open(fname) as f:
            diction = f.read().splitlines()[1:]

        diction_dict = {}
        codes = {}

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
                if skip_unused_lines(d):
                    continue

                if not d.startswith(" "):
                    from abbreviations import institute_abbr

                    x4code = d[:11].rstrip()
                    regex = r"\((.*)\)"
                    desc = re.match(regex, d[11:66]).group(1)
                    desc = convert_abbreviations(institute_abbr, desc)
                    flag = d[79:80]

                    if int(diction_num) == 3:
                        ### for DICTION 3: Institute
                        if not x4code[1:4].rstrip() == x4code[4:7]:
                            if institute_dict.get(x4code):
                                addr = institute_dict[x4code]["formatted_address"]
                                lat = institute_dict[x4code]["lat"]
                                lng = institute_dict[x4code]["lng"]
                            else:
                                addr = lat = lng = None

                        elif x4code[1:4].rstrip() == x4code[4:7]:
                            lat = country_dict[x4code[0:4].rstrip()]["country_lat"]
                            lng = country_dict[x4code[0:4].rstrip()]["country_lng"]

                        else:
                            lat = lng = None

                        codes[x4code] = {
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
                            codes[x4code] = {
                                "description": desc,
                                "pulished_country_code": journal_contry,
                                "pulished_country_name": country_dict[journal_contry][
                                    "country_name"
                                ],
                                "active": False if flag == "O" else True,
                            }

                    else:
                        codes[x4code] = {
                            "description": desc,
                            "active": False if flag == "O" else True,
                        }

        elif int(diction_num) in [144, 43, 38, 35, 34, 32, 31, 30, 6, 1]:
            for d in diction:
                skip_unused_lines(d)
                if not d.startswith(" "):
                    x4code = d[:11].rstrip()
                    desc = d[11:66].rstrip()
                    flag = d[79:80]

                    if int(diction_num) == 6:
                        ### for the DICTION   5  Reports
                        report_inst = d[59:66]
                        if institute_dict.get(report_inst):
                            codes[x4code] = {
                                "description": desc[:-7].rstrip(),
                                "publisher": report_inst,
                                "publisher_name": institute_dict[report_inst]["name"],
                                "active": False if flag == "O" else True,
                            }

                    else:
                        codes[x4code] = {
                            "description": desc,
                            "active": False if flag == "O" else True,
                        }

        elif int(diction_num) == 24:
            ### DICTION 24: Data headings
            from abbreviations import head_unit_abbr

            desc = []
            for d in diction[11:]:
                x4code = ""
                flag = ""
                desc = ""
                additional_code = ""
                if d[0].isalpha() or d[0].isdigit():
                    flag = d[79:80]  # obsolete flag
                    x4code = d[:11].rstrip()
                    desc = d[11:65].rstrip()
                    additional_code = d[65:66].rstrip()

                    if x4code.startswith("DATA") and not "ERR" in x4code:
                        additional_code = "DATA"
                    elif x4code.startswith("DATA") and "ERR" in x4code:
                        additional_code = "DATA_E"
                    elif x4code == "ERR-T":
                        additional_code = "DATA_E"

                elif d.startswith(" " * 11):
                    continue

                if x4code:
                    desc = convert_abbreviations(head_unit_abbr, "".join(desc))
                    codes[x4code] = {
                        "description": desc,
                        "additional_code": additional_code,
                        "active": False if flag == "O" else True,
                    }

        elif int(diction_num) == 25:
            ### DICTION 25: Data units
            from abbreviations import head_unit_abbr

            desc = []
            for d in diction[1:]:
                if d[0].isalpha() or d[0].isdigit():
                    flag = d[79:80]  # obsolete flag
                    x4code = d[:11].rstrip()
                    desc = d[11:44].rstrip()
                    additional_code = d[44:55].rstrip()
                    factor = d[55:66].strip()

                elif d.startswith(" " * 11):
                    continue

                if x4code:
                    desc = convert_abbreviations(head_unit_abbr, "".join(desc))
                    codes[x4code] = {
                        "description": desc,
                        "additional_code": additional_code,
                        "unit_conversion_factor": factor,
                        "active": False if flag == "O" else True,
                    }

                desc = []

        elif int(diction_num) == 144:
            ### DICTION 114: Data libraries
            from abbreviations import head_unit_abbr

            desc = []
            for d in diction[1:]:
                if d[0].isalpha() or d[0].isdigit():
                    flag = d[79:80]  # obsolete flag
                    x4code = d[:15].rstrip()
                    desc = d[15:66].rstrip()

                elif d.startswith(" " * 11):
                    continue

                if x4code:
                    desc = convert_abbreviations(head_unit_abbr, "".join(desc))
                    codes[x4code] = {
                        "description": desc,
                        "active": False if flag == "O" else True,
                    }

                desc = []

        elif int(diction_num) == 213:
            ### DICTION 25: Data units
            from abbreviations import head_unit_abbr

            desc = []
            for d in diction[1:]:
                if d[0].isalpha() or d[0].isdigit():
                    flag = d[79:80]  # obsolete flag
                    x4code = d[:11].rstrip()
                    additional_code = d[11:16].rstrip()
                    x4code3 = d[16:20].rstrip()
                    desc = d[20:66].rstrip()

                elif d.startswith(" " * 11):
                    continue

                if x4code:
                    desc = convert_abbreviations(head_unit_abbr, "".join(desc))
                    codes[x4code] = {
                        "description": desc,
                        "additional_code": additional_code,
                        "x4code3": x4code3,
                        "active": False if flag == "O" else True,
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

            from abbreviations import reaction_abbr

            cont = False
            desc = []
            for d in diction[27:]:
                if skip_unused_lines(d):
                    continue

                ### get EXFOR code
                if (
                    d[0].isalpha()
                    or d[0].isdigit()
                    or any(d.startswith(s) for s in [",", "("])
                    or not cont
                ):
                    cont = False
                    flag = d[79:80]  # obsolete flag

                    if not d.startswith(" ") and d[22] == "(":
                        ## Case 1, 2, and 3
                        x4code = d[:18].rstrip()
                        additional_code = d[18:22].rstrip()

                    elif " " not in d[:18] and d[22] != "(":
                        ## Case 4, 5
                        x4code = d[:30].rstrip()

                    elif d.startswith(" " * 18) and d[18] != " " and d[22] == "(":
                        ## Case 4, 5
                        additional_code = d[18:22].rstrip()

                    ## get description
                    if d[22] == "(":
                        desc = d[22:66].rstrip()
                        cont = True
                        if desc[-1].endswith(")"):
                            cont = False

                elif d.startswith(" " * 22):
                    desc += d[22:66].rstrip()
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
                        "active": False if flag == "O" else True,
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
