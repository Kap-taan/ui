import json
from s3 import isKeyExist, read_file_from_s3
import pandas as pd

def generate_json_analysis(file_content):

# file_path = "data/analysisBepensa1.txt"

    # Helper variables
    JOINER = "::"
    stages = ["orders", "recommendation", "sales"]
    fields_for_order = ['skucode', 'mothercode', 'quantity', 'amount']
    fields_for_recommendation = ['skucode', 'mothercode', 'quantity', 'recommendation_type', 'is_present', 'is_new', 'weight']
    fields_for_sales = ['skucode', 'mothercode', 'RNOTPreser', 'RNOTPreser1', 'RNOTPreser2', 'isNEW', 'weight']

    # Overall Variables
    total_orders = 0
    processing_date = ""
    data = {} # Key: 'loginid::outletcode', Value: {'orders': [], 'recommendation': [], 'sales': []}
    processing_records = 0

    # Variables Specific for loginid and outletcode
    outletcode = ""
    loginid = ""
    current_mode = ""
    lines_after_mode_change = 0

    # Helper functions
    def get_text_until_digit(cleaned_list):
        if len(cleaned_list) > 2:
            try:
                float(cleaned_list[1].lstrip('-'))
                return cleaned_list[1], 2
            except ValueError:
                pass

        result = []
        for i in range(1, len(cleaned_list)):
            try:
                float(cleaned_list[i].lstrip('-'))
                return " ".join(result), i
            except ValueError:
                result.append(cleaned_list[i])
        return " ".join(result), -1


    def map_fields_to_values(fields_for_sales, cleaned_list, start_index):
        mapped_data = {}

        for i in range(2, len(fields_for_sales)):
            if start_index + (i - 2) < len(cleaned_list):
                field = fields_for_sales[i]
                value = cleaned_list[start_index + (i - 2)]
                mapped_data[field] = value

        return mapped_data

    for line in file_content.splitlines():
        processing_records += 1
        
        if processing_records % 1000 == 0:
            print(f"Records processed: {processing_records}")
        
        if "--------------" in line:
            continue
        
        # Check for "Total Order today"
        if "Total Order today" in line:
            total_orders = line.split("Total Order today")[1].strip().split('"')[0]
        
        # Check for "Client date"
        if "Client date" in line:
            processing_date = line.split("Client date")[1].strip().split('"')[0]
            continue

        if "for the pair outlet:login" in line:
            tempResult = line.split("for the pair outlet:login------>")[1].strip().split('"')[0]
            outletcode = tempResult.split(JOINER)[0]
            loginid = tempResult.split(JOINER)[1]
            lines_after_mode_change = 0
            key = f"{loginid}::{outletcode}"
            if key not in data:
                data[key] = {
                    'orders': [],
                    'recommendation': [],
                    'sales': []
                }
            continue

        if "Orders are" in line:
            current_mode = "orders"
            lines_after_mode_change = 0
            continue
        
        if "Recomendations" in line:
            current_mode = "recommendation"
            lines_after_mode_change = 0
            continue
        
        if "-----> NR" in line:
            lines_after_mode_change = 0
            continue
        
        if "RNOTPreser" in line:
            current_mode = "RNOTPreser"
            lines_after_mode_change = 1
            continue
        
        if lines_after_mode_change == 1 and current_mode == "RNOTPreser":
            line = line.replace('","', '')
            list_values = line.split('"')[1].strip().split(" ")
            cleaned_list = [item for item in list_values if item and item.strip()]
            if len(cleaned_list) >= 1 and cleaned_list[0] == '---------------------------------------------------------------------------------------------':
                pass  # No action needed
            else:
                # Process sales data
                key = f"{loginid}::{outletcode}"
                sales_data = {}
                sales_data['skucode'] = cleaned_list[0]
                mothercode, index = get_text_until_digit(cleaned_list)
                sales_data['mothercode'] = mothercode
                mapped_values = map_fields_to_values(fields_for_sales, cleaned_list, index)
                sales_data.update(mapped_values)
                is_new = sales_data.get('isNEW', None)
                if is_new == '1':
                    sales_data['isNEW'] = 'true'
                elif is_new == '0':
                    sales_data['isNEW'] = 'false'
                data[key]['sales'].append(sales_data)
            continue

        if lines_after_mode_change == 1 and current_mode == "orders":
            line = line.replace('","', '')
            list_values = line.split('"')[1].strip().split(" ")
            cleaned_list = [item for item in list_values if item and item.strip()]
            if len(cleaned_list) >= 1 and cleaned_list[0] == '---------------------------------------------------------------------------------------------':
                pass  # No action needed
            else:
                # Process orders data
                key = f"{loginid}::{outletcode}"
                orders_data = {}
                orders_data['skucode'] = cleaned_list[0]
                mothercode, index = get_text_until_digit(cleaned_list)
                orders_data['mothercode'] = mothercode
                mapped_values = map_fields_to_values(fields_for_order, cleaned_list, index)
                orders_data.update(mapped_values)
                data[key]['orders'].append(orders_data)
            continue

        if lines_after_mode_change == 1 and current_mode == "recommendation":
            line = line.replace('","', '')
            list_values = line.split('"')[1].strip().split(" ")
            cleaned_list = [item for item in list_values if item and item.strip()]
            if len(cleaned_list) >= 1 and cleaned_list[0] == '---------------------------------------------------------------------------------------------':
                pass  # No action needed
            else:
                # Process recommendation data
                key = f"{loginid}::{outletcode}"
                recommendation_data = {}
                recommendation_data['skucode'] = cleaned_list[0]
                mothercode, index = get_text_until_digit(cleaned_list)
                recommendation_data['mothercode'] = mothercode
                mapped_values = map_fields_to_values(fields_for_recommendation, cleaned_list, index)
                recommendation_data.update(mapped_values)
                recommendation_type = recommendation_data.get('recommendation_type', None)
                is_present = recommendation_data.get('is_present', None)
                is_new = recommendation_data.get('is_new', None)
        
                if recommendation_type == '0':
                    recommendation_data['recommendation_type'] = 'regular'
                elif recommendation_type == '1':
                    recommendation_data['recommendation_type'] = 'cross-sell'
                elif recommendation_type == '2':
                    recommendation_data['recommendation_type'] = 'up-sell'
                
                if is_present == '1':
                    recommendation_data['is_present'] = 'true'
                elif is_present == '0':
                    recommendation_data['is_present'] = 'false'

                if is_new == '1':
                    recommendation_data['is_new'] = 'true'
                elif is_new == '0':
                    recommendation_data['is_new'] = 'false'
                data[key]['recommendation'].append(recommendation_data)
            continue

        lines_after_mode_change += 1

    return data
        
    file_path = "data/vanshika/analysisBepensa1.json"

    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)
        print(f"Records processed : {processing_records}")
        print("Json file is saved successfully")


if __name__ == "__main__":
    lob = "jnjaiph"
    date = "2024-12-05"

    key = f"dailyResponseOderReport/analysis_{lob}_{date} 00:00:00.csv"
    keyJson = f"dailyResponseOderReport/analysis_{lob}_{date} 00:00:00.json"

    isKeyPresent = isKeyExist(key)

    file_content = read_file_from_s3(key)
    data = generate_json_analysis(file_content)
