import csv
import json
from typing import Dict, List
from s3 import read_file_from_s3, isKeyExist


# Enum equivalent for User2Use
class User2Use:
    ML = "ML"
    PJP = "PJP"
    BOTH = "BOTH"
    NEW = "NEW"

# Define the UserDetails class equivalent in Python
class UserDetails:
    def __init__(self, pjp_target: float, ml_target: float, user2use: str):
        self.pjp_target = pjp_target
        self.ml_target = ml_target
        self.user2use = user2use

# Function to check if a value is between two bounds
def is_between(lower_bound: float, upper_bound: float, value: float) -> bool:
    return lower_bound <= value <= upper_bound

# Function to calculate the remaining achievement difference
def remain_ach(ach: float, target: float) -> float:
    return abs(ach - target)

# Function to convert the logic from Java to Python
def target_pjp_compliance(key: str, dynamic_threshold: float) -> Dict[str, UserDetails]:
    # Get the CSV content from S3
    csv_content = read_file_from_s3(key)

    # print(csv_content)
    # Create a CSV reader to read the data
    reader = csv.reader(csv_content.splitlines())
    user = {}

    ignore = True
    for line in reader:
        if ignore or len(line) == 1:
            ignore = False
            continue
        login_id = line[0]
        ach = float(line[1])
        if line[2] == "-1":
            user_details = UserDetails(-1, -1, User2Use.NEW)
            user[login_id] = user_details
            continue


        payload = line[9:]  # Get the payload from the 9th column onwards

        if len(payload) < 1:
            user_details = UserDetails(0.0, 0.0, User2Use.ML)
            user[login_id] = user_details
            continue

        # Join the payload and parse it as JSON
        j_payload = ",".join(payload)
        try:
            extended_attributes = json.loads(j_payload)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error parsing JSON: {e}")

        pjp_target = extended_attributes.get("pjpTarget", 0.0)
        ml_prediction = extended_attributes.get("userDetailHistory", {}).get("mlPrediction", 0.0)

        # Calculate the threshold and bounds
        threshold = ach * dynamic_threshold
        upper_bound = ach + threshold
        lower_bound = ach - threshold

        # Determine which user to use
        if is_between(lower_bound, upper_bound, pjp_target) and is_between(lower_bound, upper_bound, ml_prediction):
            user2use = User2Use.BOTH
        elif remain_ach(ach, ml_prediction) < remain_ach(ach, pjp_target):
            user2use = User2Use.ML
        else:
            user2use = User2Use.PJP

        user_details = UserDetails(pjp_target, ml_prediction, user2use)
        user[login_id] = user_details

    # Print the user details for debugging purposes
    # for u in user.items():
    #     print(f"{u[0]}----> pjpTarget: {u[1].pjp_target}, mlTarget: {u[1].ml_target}, Status: {u[1].user2use}")

    return user
