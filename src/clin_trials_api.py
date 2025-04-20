import requests
import json


# Define the DotDict class
class DotDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, dct):
        for key, value in dct.items():
            if hasattr(value, "keys"):
                value = DotDict(value)
            self[key] = value


def clinical_trials_api(condition="", terms="", intervention="", topK=5):
    # Define the URL and make the request
    url = "https://clinicaltrials.gov/api/v2/studies"

    # Define the payload for the request
    payload = {
        "query.cond": condition,
        "query.term": terms,
        "query.intr": intervention,
        "sort": "@relevance:desc",
        # "filter.overallStatus": 'COMPLETED',
    }

    studies = []
    for request_num in range(0, topK, 10):
        response = requests.get(url, params=payload)
        data = response.json()
        studies.extend(data.get("studies", []))
        if "nextPageToken" in data:
            nextPageToken = data["nextPageToken"]
            payload["pageToken"] = nextPageToken
        else:
            break

    studies = studies[:topK]

    trial_ids = []
    clinical_trial_data = []

    # Check if the request was successful
    if response.status_code == 200:
        try:
            for idx, study_data in enumerate(studies):
                study = DotDict(study_data)
                try:
                    # Get the study number (nctId)
                    nct_id = study.protocolSection.identificationModule.nctId
                    trial_ids.append("https://clinicaltrials.gov/study/" + str(nct_id))
                    clinical_trial_data.append(
                        "Clinical Trial Details #{} in Nested JSON format:".format(
                            idx + 1
                        )
                    )
                    clinical_trial_data.append(json.dumps(study))
                except (KeyError, AttributeError):
                    continue

            # Save clinical trial data as a string in results_dict
            clinical_trial_data = "\n".join(clinical_trial_data)

        except requests.exceptions.JSONDecodeError:
            print("Failed to decode JSON. Here is the raw response:")
            print(response.text)
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)

    # Print the collected clinical trial data
    print("The following top {} clinical trials are pulled:".format(topK))
    print("\n".join(trial_ids))
    # print(clinical_trial_data)

    return trial_ids, clinical_trial_data
