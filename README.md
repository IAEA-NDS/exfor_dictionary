[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/shinokumura/exfor_dictionary/main?labpath=example.ipynb)

## Introduction to the EXFOR dictionary in JSON
You may find many mysterious keywords in EXFOR entries such as:

> INSTITUTE  (1USALAS)\
> REFERENCE  (R,LA-1258,1951)\
> FACILITY   (CCW,1USALAS)\
> DETECTOR   (THRES) \
> REACTION   (2-HE-4(N,2N)2-HE-3,,SIG,,SPA)\
> STATUS     (DEP,14737002)\

These keywords are defined in the so-called EXFOR dictionary which is maintained in the IAEA Nuclear Data Section. The original format of the EXFOR dictionary is in the Fortran style fixed-width format. Each keyword is separated in the block that starts with ```DICTION```. There are 40 definitions (```DICTION```) that define such keywords. For example, you will find ```1USALAS``` means "Los Alamos National Laboratory, NM" in ```DICTION 3 Institutes```.


## EXFOR dictionary
The latest EXFOR dictionary is available at https://nds.iaea.org/nrdc/ndsx4/trans/dicts/. 
The EXFOR dictionary consists of approx. 40 definitions of types of the EXFOR codes used in identifiers,  which is the so-called DICTION. The definitions of each DICTION can be found in [DICTION   950](original/diction950.dat) which looks like as below. For example, the institute codes that are coded under INSTITUTE identifier in the BIB block are defined in [DICTION    3](original/diction3.dat). The most important DICTION would be [DICTION   236](original/diction236.dat), which defines all possible combinations of reaction strings.

```
DICTION            950     202112 List of Dictionaries            3000095000001 
  1        System identifiers                                     3000095000002 
  2        Information identifiers                                3000095000003 
  3        Institutes                                             3000095000004 
  4        Reference types                                        3000095000005 
  5        Journals                                               3000095000006 
  6        Reports                                                3000095000007 
  7        Conferences                                            3000095000008 
  8        Elements                                               3000095000009 
 15        History                                                3000095000010 
 16        Status                                                 3000095000011 
 17        Related reference types                                3000095000012 
 18        Facilities                                             3000095000013 
 19        Incident sources                                       3000095000014 
 20        Additional results                                     3000095000015 
 21        Methods                                                3000095000016 
 22        Detectors                                              3000095000017 
 23        Analyses                                               3000095000018 
 24        Data headings                                          3000095000019 
 25        Data units                                             3000095000020 
 30        Processes (REACTION SF 3)                              3000095000021 
 31        Branches (REACTION SF 5)                               3000095000022 
 32        Parameters (REACTION SF 6)                             3000095000023 
 33        Particles                                              3000095000024 
 34        Modifiers (REACTION SF 8)                              3000095000025 
 35        Data types (REACTION SF 9)                             3000095000026 
 37        Results                                                3000095000027 
 38        Supplemental information                               3000095000028 
 43        NLIB for evaluated libraries                           3000095000029 
 45        New CINDA quantities                                   3000095000030 
 47        Old / New CINDA quantities                             3000095000031 
 48        Alphabetic energy values                               3000095000032 
 52        CINDA readers                                          3000095000033 
113        Web quantities                                         3000095000034 
144        Data libraries                                         3000095000035 
207        Books                                                  3000095000036 
209        Compounds                                              3000095000037 
213        Reaction types                                         3000095000038 
227        Nuclides and nat.isot.mixtures                         3000095000039 
235        Work types                                             3000095000040 
236        Quantities (REACTION SF 5-8)                           3000095000041 
ENDDICTION          40          0                                 3000095099999 
```


## EXFOR dictionary parser
The EXFOR dictionary parser, ``exfor_dictionary.py``, will download the latest dictionary, trans.9***,  every time it runs and the parser divides it into the unit of DICTION and store original format files in ``original`` directory and JSON converted files in ``json`` directory. While conversion, many abbreviations in the description will be expanded. You can check the [DICTION   236](json/diction236.json).

Note that because of the EXFOR dictionary's troublesome formats, parsing all information is not yet possible. Currently, JSON files include information that can be parsed and used for the main EXFOR parser. 


## How to use
See [.ipynb file](https://github.com/shinokumura/exfor_dictionary/blob/main/example.ipynb) If you don't have Jupyter notebook environment, you can run it from Binder from the following button. [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/shinokumura/exfor_dictionary/main?labpath=example.ipynb)



## EXFOR dictionary parser API
The API will be available soon, please ask API KEY to use it.

```
import requests
import json

url = "https://data.mongodb-api.com/app/data-qfzzc/endpoint/data/beta/action/findOne"

payload = json.dumps(
    {
        "collection": "dictionary",
        "database": "exfor",
        "dataSource": "exparser",
        "filter": {"diction_num": "236"},
        "projection": {"_id": 0, "diction_num": 1, "diction_def": 1, "parameters": 1},
    }
)
headers = {
    "Content-Type": "application/json",
    "Access-Control-Request-Headers": "*",
    "api-key": <API-KEY>,
}

response = requests.request("POST", url, headers=headers, data=payload)
print(json.dumps(response.json(), indent=2))
```