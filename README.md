[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/shinokumura/exfor_dictionary/main?labpath=example.ipynb)

## Introduction to the EXFOR dictionary in JSON
You may find many mysterious keywords in EXFOR entries such as:

> INSTITUTE  (1USALAS)\
> REFERENCE  (R,LA-1258,1951)\
> FACILITY   (CCW,1USALAS)\
> DETECTOR   (THRES) \
> REACTION   (2-HE-4(N,2N)2-HE-3,,SIG,,SPA)\
> STATUS     (DEP,14737002)\

These keywords are defined in the EXFOR dictionary which is maintained in the IAEA Nuclear Data Section. This repository provides the JSON-converted-EXFOR-dictionary file. [Latest file](json/trans.9127.json)



## EXFOR dictionary
The EXFOR dictionary consists of approx. 40 definitions of identifiers, so-called ```DICTION```. The original EXFOR dictionary format is in the FORTRAN style fixed-width format. Each block starts with ```DICTION``` and keywords (EXFOR codes) are defined with small descriptions in the ```DICTION``` block. All keywords (EXFOR codes) in EXFOR belong to the certain identifier. For example, you will find ```1USALAS```, which means "Los Alamos National Laboratory, NM", in ```DICTION 3 Institutes```. All definitions of identifiers (```DICTION```) can be found in ```DICTION   950```. 

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
 17        Related reference types                      
 18        Facilities                                   
 19        Incident sources                             
 20        Additional results                           
 21        Methods                                      
 22        Detectors                                    
 23        Analyses                                     
 24        Data headings                                
 25        Data units                                   
 30        Processes (REACTION SF 3)                    
 31        Branches (REACTION SF 5)                     
 32        Parameters (REACTION SF 6)                   
 33        Particles                                    
 34        Modifiers (REACTION SF 8)                    
 35        Data types (REACTION SF 9)                   
 37        Results                                      
 38        Supplemental information                     
 43        NLIB for evaluated libraries                 
 45        New CINDA quantities                         
 47        Old / New CINDA quantities                   
 48        Alphabetic energy values                     
 52        CINDA readers                                
113        Web quantities                               
144        Data libraries                               
207        Books                                        
209        Compounds                                    
213        Reaction types                               
227        Nuclides and nat.isot.mixtures               
235        Work types                                   
236        Quantities (REACTION SF 5-8)                 
ENDDICTION          40          0                       
```



## Use JSON format EXFOR dictionary
See [.ipynb file](https://github.com/IAEA-NDS/exfor_dictionary/blob/main/example.ipynb) 

If you don't have Jupyter notebook environment, you can run it on Binder from the following button. [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/IAEA-NDS/exfor_dictionary/main?labpath=example.ipynb)

```
import json
# Latest dictionary sequential number
latest = "9127"

# latest number of dictionary file (see trans_backup/trans.****)
j = open("json/trans." + latest + ".json")
exfor_dictionary = json.load(j)
```

To check what DICTION contain what kind of information:

```
for i, k in exfor_dictionary["definitions"].items():
    print(i, "-->   ", k["description"])
```

To see what is ```INSTITUTE  (1USALAS)```:

```
print(json.dumps(exfor_dictionary["dictionaries"]["3"]["codes"]["1USALAS"], indent = 2))
```


## EXFOR dictionary parser
The EXFOR dictionary parser, ``exfor_dictionary.py``, will download the latest dictionary file from [IAEA NDS website](https://nds.iaea.org/nrdc/ndsx4/trans/dicts/). The parser divides it into the unit of DICTION and store original format files in ``original`` directory and JSON converted files in ``json`` directory. While conversion, some abbreviations in the description are replaced.

The EXFOR dictionary is updated irregular basis, so if you need to run the update of EXFOR dictionary to convert new file into JSON format, please run:

```
python convert_dictionary.py
```

Parsing all information is not yet perfect. Currently, JSON files are produced for some of ```DICTION``` with information that are used in the EXFOR parser. 





## Contact
nds.contact-point@iaea.org