
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/IAEA-NDS/exfor_dictionary/main?labpath=example/example.ipynb)

# Introduction to the EXFOR Dictionary in JSON

EXFOR entries contain a variety of keywords, for example:

> INSTITUTE  (1USALAS)
> REFERENCE  (R,LA-1258,1951)
> FACILITY   (CCW,1USALAS)
> DETECTOR   (THRES)
> REACTION   (2-HE-4(N,2N)2-HE-3,,SIG,,SPA)
> STATUS     (DEP,14737002)

These keywords are defined in the **EXFOR dictionary**, which is maintained by the IAEA Nuclear Data Section.
This repository provides a JSON-converted version of the dictionary: [latest file](src/exfor_dictionary/latest.json).

---

## Structure of the EXFOR Dictionary

The EXFOR dictionary contains approximately 40 categories of identifiers, called **`DICTION` blocks**.
The original dictionary is stored in a fixed-width FORTRAN-style format.

Each `DICTION` block begins with the keyword `DICTION` and contains a list of EXFOR codes along with descriptions.
For instance, the code `1USALAS` corresponds to *Los Alamos National Laboratory, NM* and is defined in `DICTION 3 Institutes`.

All dictionary identifiers are summarized in `DICTION 950`. A shortened example:

```
DICTION            950     202112 List of Dictionaries  
  1        System identifiers                           
  2        Information identifiers                      
  3        Institutes                                   
  4        Reference types                              
  5        Journals                                     
  6        Reports                                      
  7        Conferences                                  
  8        Elements                                     
 15        History                                      
 16        Status                                       
 18        Facilities                                   
 22        Detectors                                    
 30        Processes (REACTION SF 3)                    
 33        Particles                                    
 37        Results                                      
113        Web quantities                               
144        Data libraries                               
227        Nuclides and nat.isot.mixtures               
236        Quantities (REACTION SF 5-8)                 
ENDDICTION          40          0                       
```

---

## Using the JSON-Formatted EXFOR Dictionary

An example Jupyter notebook is available here:
📓 [example.ipynb](https://github.com/IAEA-NDS/exfor_dictionary/blob/main/example/example.ipynb)

If you do not have a local Jupyter environment, you can launch the example directly in Binder:
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/IAEA-NDS/exfor_dictionary/main?labpath=example/example.ipynb)

### Example usage in Python

```python
import json

# Load the latest EXFOR dictionary
with open("src/exfor_dictionary/latest.json") as j:
    exfor_dictionary = json.load(j)
```

List all available `DICTION` categories:

```python
for i, k in exfor_dictionary["definitions"].items():
    print(i, "-->", k["description"])
```

Inspect a specific keyword, e.g. `INSTITUTE (1USALAS)`:

```python
import json
print(json.dumps(
    exfor_dictionary["dictionaries"]["3"]["codes"]["1USALAS"], 
    indent=2
))
```

---

## EXFOR Dictionary Parser

The parser script [`exfor_dictionary.py`](exfor_dictionary.py) automatically downloads the latest EXFOR dictionary from the [IAEA NDS website](https://nds.iaea.org/nrdc/ndsx4/trans/dictionaries/).

It processes the source file into `DICTION` blocks, storing:

* the original format in the `original/` directory
* the JSON-converted version in the `json/` directory

During conversion, some abbreviations in descriptions are expanded for clarity.

Since the EXFOR dictionary is updated irregularly, you can re-run the conversion using:

```bash
python convert_dictionary.py
```

⚠️ **Note**: The IAEA-NDS "Open Area" is currently password-protected. To update the dictionary, you must set your credentials as environment variables:

```bash
export OPENAREA_USER=<username>
export OPENAREA_PWD=<password>
```

---

## Current Status

* Parsing is still under development.
* JSON files are currently generated only for selected `DICTION` blocks relevant to the EXFOR parser.
* Further improvements are ongoing.

---

## Contact

For questions or feedback, please contact:
📧 **[nds.contact-point@iaea.org](mailto:nds.contact-point@iaea.org)**
