import csv
import os
from twilio.rest import Client
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv(override=True)


account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

twilio_numbers_str = os.getenv("TWILIO_PHONE_NUMBERS")
if twilio_numbers_str:
    twilio_numbers = [num.strip() for num in twilio_numbers_str.split(',')]
else:
    twilio_numbers = []

url = os.getenv("TWILIO_URL")
print(f"Twilio URL: {url}")
def load_phone_numbers_from_csv(file_path):
    phone_numbers = []
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get('phone_number'):
                    phone_numbers.append(row['phone_number'].strip())
        return phone_numbers
    except Exception as e:
        print(f"Error reading CSV file '{file_path}': {e}")
        return []


phone_numbers_file = "numbers.csv"
target_phone_numbers = load_phone_numbers_from_csv(phone_numbers_file)


def initiate_call(target_phone_number, source_number):
    try:
        call = client.calls.create(
            url=url,  # URL from environment variable
            to=target_phone_number,
            from_=source_number,
            status_callback=f"{url}/call_status",  
            status_callback_method="POST",
            status_callback_event=["initiated", "ringing", "answered", "completed"]
        )
        print(f"Call initiated to {target_phone_number} from {source_number}. Call SID: {call.sid}")
        return call.sid
    except Exception as e:
        print(f"Error initiating call to {target_phone_number} from {source_number}: {e}")
        return None


def main_call_initiation():
    # Assuming target_phone_numbers is already loaded from CSV (or elsewhere)
    unique_targets = list(set(target_phone_numbers))
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i, target in enumerate(unique_targets):
            # Cycle through Twilio numbers
            source = twilio_numbers[i % len(twilio_numbers)]
            futures.append(executor.submit(initiate_call, target, source))
        for fut in futures:
            sid = fut.result()
            if sid:
                print(f"Call SID: {sid}")

if __name__ == "__main__":
    main_call_initiation()
