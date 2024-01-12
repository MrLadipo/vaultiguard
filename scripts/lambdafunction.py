import json
import boto3
import os
from datetime import datetime


def lambda_handler(event, context):
    print("Event:", event)
    # Log the entire event for debugging
    print("Received event:", json.dumps(event))

    client = boto3.client("dynamodb")
    sns = boto3.client("sns")
    sns_topic_arn = os.environ.get("SNS_TOPIC_ARN")

    parsed_datetime = datetime.fromisoformat(event["datetime"])
    formatted_date = parsed_datetime.strftime("%b %d, %Y %I:%M %p")

    def interpret_attribute(attribute, value):
        notification_mapping = {
            "Temperature": ["LOW", "OK", "HIGH"],
            "Humidity": ["LOW", "OK", "HIGH"],
            "Internal Air Quality (IAQ)": [
                "POOR IAQ",
                "EXCELLENT",
                "OK",
                "Very POOR IAQ",
            ],
        }

        response_action_mapping = {
            "Temperature": ["Adjust HVAC Heating", "NONE", "Adjust HVAC Heating"],
            "Humidity": ["Adjust HVAC Ventilation", "NONE", "Adjust HVAC Ventilation"],
            "Internal Air Quality (IAQ)": [
                "Activate HVAC AQC",
                "NONE",
                "Activate HVAC AQC",
            ],
        }

        notification_index = -1
        action_index = -1

        if attribute == "Temperature":
            if value >= 0 and value <= 14:
                notification_index = 0  # LOW / POOR IAQ
                action_index = 0  # Adjust HVAC Heating
            elif value >= 15 and value <= 25:
                notification_index = 1  # OK
                action_index = 1  # NONE
            elif value >= 26 and value <= 100:
                notification_index = 2  # HIGH / V-POOR IAQ
                action_index = 2  # Adjust HVAC Heating

        elif attribute == "Humidity":
            if value >= 0 and value <= 29:
                notification_index = 0  # LOW / POOR IAQ
                action_index = 0  # Adjust HVAC Ventilation
            elif value >= 30 and value <= 59:
                notification_index = 1  # OK
                action_index = 1  # NONE
            elif value >= 60 and value <= 100:
                notification_index = 2  # HIGH / V-POOR IAQ
                action_index = 2  # Adjust HVAC Ventilation

        elif attribute == "Internal Air Quality (IAQ)":
            if value >= 0 and value <= 25:
                notification_index = 1  # EXCELLENT
                action_index = 1  # NONE
            elif value >= 26 and value <= 50:
                notification_index = 2  # OK
                action_index = 1  # NONE
            elif value >= 51 and value <= 74:
                notification_index = 0  # LOW / POOR IAQ
                action_index = 0  # Activate HVAC AQC
            elif value >= 75 and value <= 100:
                notification_index = 3  # HIGH / V-POOR IAQ
                action_index = 2  # Activate HVAC AQC

        notification = notification_mapping[attribute][notification_index]
        action = response_action_mapping[attribute][action_index]

        return notification, action

    # Example usage:
    temperature = event["temperature"]
    humidity = event["humidity"]
    iaq = event["iaq"]

    temperature_notification, temperature_action = interpret_attribute(
        "Temperature", temperature
    )
    humidity_notification, humidity_action = interpret_attribute("Humidity", humidity)
    iaq_notification, iaq_action = interpret_attribute(
        "Internal Air Quality (IAQ)", iaq
    )

    print(
        "Temperature Notification:",
        temperature_notification,
        "Action:",
        temperature_action,
    )
    print("Humidity Notification:", humidity_notification, "Action:", humidity_action)
    print("IAQ Notification:", iaq_notification, "Action:", iaq_action)

    def status_check():
        if (
            temperature_notification == "OK"
            and humidity_notification == "OK"
            and (iaq_notification == "OK" or iaq_notification == "EXCELLENT")
        ):
            status = "OPTIMAL"
        elif (
            (temperature_notification == "LOW" or humidity_notification == "LOW")
            and (iaq_notification == "OK" or iaq_notification == "EXCELLENT")
            and temperature_notification != "HIGH"
            and humidity_notification != "HIGH"
        ):
            status = "WARNING"
        elif (
            temperature_notification == "HIGH"
            or humidity_notification == "HIGH"
            or iaq_notification == "POOR IAQ"
            or iaq_notification == "Very POOR IAQ"
        ):
            status = "ALARM"
        return status

    env_status = status_check()
    print("The environmental status of your vault is: ", env_status)
    # Extract data from the parsed JSON payload

    try:
        response = client.put_item(
            TableName="group4table",
            Item={
                "thingid": {"S": event["thingid"]},
                "datetime": {"S": event["datetime"]},
                "temperature": {"N": str(event["temperature"])},
                "humidity": {"N": str(event["humidity"])},
                "iaq": {"N": str(event["iaq"])}
                # "t_notification": {"S": temperature_notification},
                # "t_action": {"S": temperature_action},  # Corrected variable name
                # "h_notification": {
                #     "S": humidity_notification
                # },  # Include humidity values if needed
                # "h_action": {"S": humidity_action},
                # "iaq_notification": {
                #     "S": iaq_notification
                # },  # Include IAQ values if needed
                # "iaq_action": {"S": iaq_action},
                # "status": {"S": env_status},
            },
        )
        print("DynamoDB response:", response)

        email_message = (
            f"Environmental Status within Vaulticore as at {formatted_date} (GMT).\n\n"
            f"Overall Environmental Status: {env_status}\n\n"
            "Environmental Conditions:\n"
            f"- Temperature: {temperature_notification} ({temperature}\u00B0C)\n"
            f"- Humidity: {humidity_notification} ({humidity}%).\n"
            f"- IAQ: {iaq_notification} ({iaq} IAQ).\n\n"
            "Response Actions:\n"
            f"- For Temperature: {temperature_action}\n"
            f"- For Humidity: {humidity_action}\n"
            f"- For IAQ: {iaq_action}\n"
        )

        print(email_message)

        if env_status == "ALARM":
            newresponse = sns.publish(
                TopicArn=sns_topic_arn,
                Message=email_message,
                Subject="Environmental Status Alarm Protocol",
            )
            print("SNS response:", newresponse)

    except Exception as e:
        print("Error:", e)
