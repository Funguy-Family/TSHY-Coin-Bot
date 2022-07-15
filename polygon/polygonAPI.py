import requests
import json
import locale

class MakeApiCall():

    def get_data(self, api):
        response = requests.get(f"{api}")
        if response.status_code == 200:
            print("sucessfully fetched the data")
            self.formatted_print(response.json())
        else:
            print(
                f"Hello person, there's a {response.status_code} error with your request")

    def get_user_data(self, api, parameters):
        response = requests.get(f"{api}", params=parameters)
        if response.status_code == 200:
            self.tuschay_coin = int(response.json()["result"])
            self.tuschay_coin = self.tuschay_coin/(10**18)
        else:
            self.tuschay_coin = -1

    def formatted_print(self, obj):
        return json.dumps(obj, sort_keys=True, indent=4)

    def __init__(self, api, module, action, contractaddress, address):

        f = open('credentials/polygon.json')
        credentialData = json.load(f)    

        parameters = {
            "module": module,
            "action": action,
            "contractaddress": contractaddress,
            "address": address,
            "tag": "latest",
            "apikey": credentialData["api_key"]
        }

        self.get_user_data(api, parameters)

        locale.setlocale( locale.LC_ALL, '' )
        self.tuschay_coin = locale.currency(self.tuschay_coin, grouping=True)

        # print(self.tuschay_coin)

if __name__ == "__main__":
    api_call = MakeApiCall(
        "https://api.polygonscan.com/api",
        "account",
        "tokenbalance",
        "0xD8f9a909649BA317175A4f2F5416958Af64a0BFC",
        "0xf7ea4da94ef718db72e96f692be43236feb36ece"
    )
    api_call = MakeApiCall(
        "https://api.polygonscan.com/api",
        "account",
        "tokenbalance",
        "0xD8f9a909649BA317175A4f2F5416958Af64a0BFC",
        "0x9e1f42c1c9443ddcd59adc7a5aaf82164d959ffe"
    )
    api_call = MakeApiCall(
        "https://api.polygonscan.com/api",
        "account",
        "tokenbalance",
        "0xD8f9a909649BA317175A4f2F5416958Af64a0BFC",
        "0xf6b738a8fef757e7b14408ef6a71a4b02e857171"
    )

