import requests
import json
import os

DATA_BASE_URL="https://raw.githubusercontent.com/fgeorges/star-wars-dataset/master/json/people/"
DATA_TOTAL = 88
DATA_FOLDER = "./json"
GRAPHQL_URL=os.getenv("GRAPHQL_URL")
GRAPHQL_API_KEY=os.getenv("GRAPHQL_API_KEY")

def download_data():
    if not os.path.exists(DATA_FOLDER):
        os.mkdir(DATA_FOLDER)

    for i in range(1, DATA_TOTAL+1):
        if not os.path.exists("{}/{}.json".format(DATA_FOLDER, str(i))):
            url = DATA_BASE_URL + str(i) + ".json"
            r = requests.get(url)
            with open("json/" + str(i) + ".json", "w") as f:
                f.write(r.text)

def load_data():
    characters_data = []
    for i in range(1, DATA_TOTAL+1):
        if not os.path.exists("{}/{}.json".format(DATA_FOLDER, str(i))):
            print("File not found: {}.json".format(i))
            continue

        file_name = "{}/{}.json".format(DATA_FOLDER, str(i))
        with open(file_name, "r") as f:
            try:
                data = json.load(f)["people"]            
                payload = {
                    "name": data["name"],
                "height": data["height"] if "height" in data else 0,
                "birth_year": data["birth_year"] if "birth_year" in data else None,
                "gender": data["gender"] if "gender" in data else "unknown",
                "description": "".join(data["desc"]).replace("\"", "'") if "desc" in data else None
                }
                print(payload)
                characters_data.append(payload)
            except Exception as e:
                print("Error on processing {} — {}".format(f,e))                
    return characters_data

def create_data(payload):
    body = '''
        mutation Create{{
            createCharacter(name: "{name}", height: {height}, birth_year: "{birth_year}", gender: {gender}, description: "{description}"){{
                id
            }}
        }}
        '''.format(**payload)
    print(body)
    headers={
        "x-api-key": GRAPHQL_API_KEY
    }
    r = requests.post(GRAPHQL_URL, json={'query': body, 'variables': payload}, headers=headers)
    print(r.json())
    

if __name__ == "__main__":
    download_data()
    characters_data = load_data()
    for character in characters_data:
        create_data(character)