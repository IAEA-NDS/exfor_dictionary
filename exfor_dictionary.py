####################################################################
#
# This file is a part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Disclaimer: The code is still under developments and not ready
#             to use. It has been made public to share the progress
#             among collaborators.
# Contact:    nds.contact-point@iaea.org
#
####################################################################

import os
import json

try:
    from config import DICTIONARY_PATH, LATEST_TRANS

except:
    import sys
    sys.path.append("../exfor_dictionary/")
    from exfor_dictionary.config import DICTIONARY_PATH, LATEST_TRANS


###################################################################
###
###   For exfor_parser
###
###################################################################
class Diction:
    def __init__(self, diction_num=None):
        self.latest_trans = LATEST_TRANS  # get_latest_trans_num(get_local_trans_nums())
        self.dictionaries = self.read_latest_dictionary()
        self.diction_num = diction_num


    def read_latest_dictionary(self):
        file = os.path.join(
            DICTIONARY_PATH, "json", "trans." + str(self.latest_trans) + ".json"
        )
        with open(file) as json_file:
            return json.load(json_file)["dictionaries"]

    def get_diction(self):
        return self.dictionaries[self.diction_num]["codes"]


    def get_incident_en_heads(self):
        ## diction 24: Data heads, get_x
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "A"
            and diction["codes"][h]["active"]
            and "-DN" not in h
            and "-NM" not in h
        ]


    def get_incident_en_err_heads(self):
        ## diction 24: Data heads, get_dx
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "B"
            and diction["codes"][h]["active"]
            and "-DN" not in h
            and "-NM" not in h
        ]


    def get_data_heads(self):
        ## diction 24: Data heads, for y
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "DATA"
            and diction["codes"][h]["active"]
            and "-DN" not in h
            and "-NM" not in h
        ]


    def get_data_err_heads(self):
        ## diction 24: Data heads, for d_y
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "DATA_E"
            and diction["codes"][h]["active"]
            and "-DN" not in h
            and "-NM" not in h
        ]


    def get_outgoing_e_heads(self):
        ## diction 24: Data heads, measured energy E or E-LVL
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "E"
            and diction["codes"][h]["active"]
        ]


    def get_outgoing_e_err_heads(self):
        ## diction 24: Data heads, measured energy  E-ERR E-LVL-ERR
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "F"
            and diction["codes"][h]["active"]
        ]


    def get_level_heads(self):
        ## diction 24: Data heads, measured level
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "L"
            and diction["codes"][h]["active"]
        ]


    def get_angle_heads(self):
        ## diction 24: Data heads, measured level
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "G"
            and diction["codes"][h]["active"]
        ]


    def get_angle_err_heads(self):
        ## diction 24: Data heads, measured level
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "H"
            and diction["codes"][h]["active"]
        ]


    def get_mass_heads(self):
        ## diction 24: Data heads, get_x
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "J"
            and diction["codes"][h]["active"]
        ]


    def get_elem_heads(self):
        ## diction 24: Data heads, get_x
        diction = self.dictionaries["24"]
        return [
            h
            for h in diction["codes"].keys()
            if diction["codes"][h]["additional_code"] == "I"
            and diction["codes"][h]["active"]
        ]


    def get_details(self, diction_num, key):
        diction = self.dictionaries[diction_num]["codes"]

        if diction.get(key):
            return diction[key]["description"]
        else:
            return None


    def get_unit_factor(self, datahead):
        ## diction 25: Data units
        diction = self.dictionaries["25"]
        if " " in datahead:
            ## ENTRY 40234003 contains "SEE TEXT" in the units
            return 1.0
        else:
            factor = diction["codes"][datahead][
                "unit_conversion_factor"
            ]  # if diction[datahead]["active"]
            if factor == "":
                return 1.0
            else:
                return factor


    def get_standard_unit(self, unit):
        diction = self.dictionaries["25"]

        additional_code = diction["codes"][unit]["additional_code"]

        for unit_code in diction["codes"]:
            if (
                additional_code == diction["codes"][unit][additional_code]
                and diction["codes"][unit]["unit_conversion_factor"] == 1
            ):
                standard_unit = unit

        if standard_unit == "":
            return unit
        else:
            return standard_unit

    def get_institute(self, code):
        diction = self.dictionaries["3"]

        return diction["codes"][code.replace("(", "").replace(")", "").strip()][
            "description"
        ]

    def get_reftype(self, code):
        diction = self.dictionaries["4"]

        return diction["codes"][code.replace("(", "").replace(")", "").strip()][
            "description"
        ]

    def get_journal(self, code):
        diction = self.dictionaries["5"]

        return diction["codes"][code.replace("(", "").replace(")", "").strip()][
            "description"
        ]

    def get_report(self, code):
        diction = self.dictionaries["6"]

        return diction["codes"][code.replace("(", "").replace(")", "").strip()][
            "description"
        ]

    def get_confproceeding(self, code):
        diction = self.dictionaries["7"]

        return diction["codes"][code.replace("(", "").replace(")", "").strip()][
            "description"
        ]

    def get_method(self, code):
        diction = self.dictionaries["21"]

        return diction["codes"][code.replace("(", "").replace(")", "").strip()][
            "description"
        ]

    def get_detectors(self, code):
        diction = self.dictionaries["22"]

        return diction["codes"][code.replace("(", "").replace(")", "").strip()][
            "description"
        ]

    def get_facility(self, code):
        diction = self.dictionaries["18"]

        return diction["codes"][code.replace("(", "").replace(")", "").strip()][
            "description"
        ]

    def get_err_analysis(self, code):
        diction = self.dictionaries["24"]

        return diction["codes"][code.replace("(", "").replace(")", "").strip()][
            "description"
        ]

    def get_inc_sources(self, code):
        diction = self.dictionaries["19"]

        return diction["codes"][code.replace("(", "").replace(")", "").strip()][
            "description"
        ]


