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
import os

DICTIONARY_URL = "https://nds.iaea.org/nrdc/ndsx4/trans/dictionaries/"


if os.path.exists("src/exfor_dictionary/trans_backup") and os.path.exists("src/exfor_dictionary/trans_json") :
    DICTIONARY_PATH = "src/exfor_dictionary/"

else:
    from importlib.resources import files
    DICTIONARY_PATH = files("exfor_dictionary")

print(DICTIONARY_PATH)


PICKLE_PATH = os.path.join(DICTIONARY_PATH, "pickles")



