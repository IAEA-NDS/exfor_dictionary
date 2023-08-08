import requests
import json
import datetime
import time

from exfor_dictionary import conv_dictionary_to_json


base_url = "https://127.0.0.1:5000/"
# token = "?access_token=" + "hVnMkNFoWfRCh5zZvU4DXRjPQZVJhO02oYjKzZ855fCecARKKd4XE0L9lzCz"
# token = "?access_token=" + "GGP3cy9oeKtmgAH3eAT2ljf8dSXCMn2dOs6WawQZi5jxAGqwyWN44igOSA99"


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
    + datetime.datetime.now().strftime("%A%a%B%b"),
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://127.0.0.1:5000",
    # "Content-Type": "application/octet-stream"
    "content-type": "application/json",
    "charset": "utf-8",
}


dict_dict = {
    "diction_num": "18",
    "x4code": "(REAC)",
    "details": "detailsdetailsdetailsdetailsdetailsdetails",
    "additional_code": "nothing additional_code",
    "active": True,
}


def post_x4dictionary():
    url = base_url + "api/dictionaries/" + token

    exfor_dictionary = conv_dictionary_to_json("9126")

    for d in exfor_dictionary["dictionaries"].keys():
        for key, item in exfor_dictionary["dictionaries"][d]["codes"].items():
            dict_dict = {
                "diction_num": str(d),
                "x4code": key,
                "details": item["description"],
                "additional_code": item["additional_code"]
                if item.get("additional_code")
                else "",
                "active": item["active"],
            }
            print(dict_dict)
            r = requests.post(
                url,
                data=json.dumps(dict_dict),
                headers=headers,
                verify=False,  # , stream=True
            )

            if r.status_code == 429:
                print(r, r.json(), r.headers["Retry-After"])
                time.sleep(int(r.headers["Retry-After"]))
                r = requests.post(
                    url,
                    data=json.dumps(dict_dict),
                    headers=headers,
                    verify=False,  # , stream=True
                )


post_x4dictionary()
