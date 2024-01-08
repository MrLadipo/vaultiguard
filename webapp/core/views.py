from django.shortcuts import render
import boto3

# import datetime
from datetime import datetime


def refresh_dynamodb_client():
    return boto3.client("dynamodb", region_name="us-east-1")


dynamodb_client = refresh_dynamodb_client()
# current_datetime = datetime.utcnow().isoformat()


def result(request):
    # DynamoDB setup
    table_name = "group4table"
    # dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")
    # dynamodb_client = refresh_dynamodb_client()

    try:
        # Query to get most recent data
        response = dynamodb_client.query(
            TableName=table_name,
            Limit=1,
            KeyConditionExpression="thingid = :pk_value",
            ExpressionAttributeValues={
                ":pk_value": {"S": "vaulticore_ags_sensor_01"},
            },
            ScanIndexForward=False,  # To retrieve data in reverse order
        )

        # Check if there are items returned
        if "Items" in response:
            most_recent_item = response["Items"][0]
            item_date = most_recent_item["datetime"]["S"]
            temperature = most_recent_item["temperature"]["N"]
            humidity = most_recent_item["humidity"]["N"]
            iaq = most_recent_item["iaq"]["N"]
            date_strptime = datetime.strptime(
                item_date, "%Y-%m-%dT%H:%M:%S.%f"
            ).strftime("%Y-%m-%d %I:%M:%S %p")
        else:
            most_recent_item = None  # No items found
    except Exception as e:
        print(f"Error: {e}")
        most_recent_item = None  # Handle errors gracefully

    temp_reading = int(temperature)
    temp_response = None
    if temp_reading <= 14:
        temp_interpretation = "Low / Poor IAQ"
        temp_badge = "warning"
        temp_response = "Adjust HVAC Heating"
    elif temp_reading >= 15 and temp_reading <= 25:
        temp_interpretation = "OK"
        temp_badge = "success"
    elif temp_reading >= 26 and temp_reading <= 100:
        temp_interpretation = "High / V-Poor IAQ"
        temp_badge = "danger"
        temp_response = "Adjust HVAC Heating"
    else:
        temp_interpretation = None

    humidity_reading = int(humidity)
    humidity_response = None
    if humidity_reading <= 29:
        humidity_interpretation = "Low / Poor IAQ"
        humidity_badge = "warning"
        humidity_response = "Adjust HVAC Ventilation"
    elif humidity_reading >= 30 and humidity_reading <= 59:
        humidity_interpretation = "OK"
        humidity_badge = "success"
    elif humidity_reading >= 60 and humidity_reading <= 100:
        humidity_interpretation = "High / V-Poor IAQ"
        humidity_badge = "danger"
        humidity_response = "Adjust HVAC Ventilation"
    else:
        humidity_interpretation = None

    iaq_reading = int(iaq)
    iaq_response = None
    if iaq_reading >= 51 and iaq_reading <= 74:
        iaq_interpretation = "Low / Poor IAQ"
        iaq_badge = "danger"
        iaq_response = "Activate HVAC AQC"
    elif iaq_reading >= 0 and iaq_reading <= 25:
        iaq_interpretation = "Excellent"
        iaq_badge = "success"
    elif iaq_reading >= 26 and iaq_reading <= 50:
        iaq_interpretation = "Good"
        iaq_badge = "success"
    elif iaq_reading >= 75 and iaq_reading <= 100:
        iaq_interpretation = "High / V-Poor IAQ"
        iaq_badge = "danger"
        iaq_response = "Activate HVAC AQC"
    else:
        iaq_interpretation = None

    if (
        temp_interpretation == "OK"
        and humidity_interpretation == "OK"
        and iaq_interpretation == "Excellent"
        or iaq_interpretation == "Good"
    ):
        overall_status = "OPTIMAL"
        status_badge = "success"
    elif temp_badge or humidity_badge or iaq_badge == "danger":
        overall_status = "ALARM"
        status_badge = "danger"
    elif temp_badge == "warning" or humidity_interpretation == "warning":
        overall_status = "WARNING"
        status_badge = "warning"
    """ else:
        overall_status = "WARNING"
        status_badge = "warning"
     """

    context = {
        "most_recent_item": most_recent_item,
        "date_strptime": date_strptime,
        "temperature": temperature,
        "temp_interpretation": temp_interpretation,
        "temp_badge": temp_badge,
        "temp_response": temp_response,
        "humidity": humidity,
        "humidity_interpretation": humidity_interpretation,
        "humidity_badge": humidity_badge,
        "humidity_response": humidity_response,
        "iaq": iaq,
        "iaq_interpretation": iaq_interpretation,
        "iaq_badge": iaq_badge,
        "iaq_response": iaq_response,
        "overall_status": overall_status,
        "status_badge": status_badge,
    }
    return render(request, "index.html", context)


def historical_readings(request):
    # DynamoDB setup
    table_name = "group4table"
    dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")

    try:
        # Query to get historical readings
        response = dynamodb_client.query(
            TableName=table_name,
            Limit=30,
            KeyConditionExpression="thingid = :pk_value",
            ExpressionAttributeValues={":pk_value": {"S": "vaulticore_ags_sensor_01"}},
            ScanIndexForward=False,
        )

        # Check if there are items returned
        if "Items" in response:
            historical_readings = response["Items"]
            historical_readings.sort(key=lambda x: x["datetime"]["S"], reverse=True)
            for v in historical_readings:
                item_date = v["datetime"]["S"]
                formatted_date = datetime.strptime(
                    item_date, "%Y-%m-%dT%H:%M:%S.%f"
                ).strftime("%Y-%m-%d %I:%M:%S %p")
                v["formatted_date"] = formatted_date  # Add formatted date to each item
        else:
            historical_readings = []  # No items found
    except Exception as e:
        print(f"Error: {e}")
        historical_readings = []  # Handle errors gracefully

    # Pass data to template
    context = {"historical_readings": historical_readings}
    return render(request, "historical_readings.html", context)
