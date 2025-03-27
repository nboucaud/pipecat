from twilio.rest import Client
import time

# Your Twilio Account SID and Auth Token
account_sid = ''
auth_token = ''
client = Client(account_sid, auth_token)

# Details for the calls
twilio_phone_number = '+13322392611'  # Your Twilio phone number
url = 'https://f452-34-82-42-179.ngrok-free.app/'  # Your server's URL

# Read phone numbers from the file `numbers.txt`
def load_phone_numbers_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            # Read all lines and strip whitespace/newlines
            phone_numbers = [line.strip() for line in file.readlines()]
            return phone_numbers
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return []

# Load phone numbers from `numbers.txt`
phone_numbers_file = "numbers.txt"
target_phone_numbers = load_phone_numbers_from_file(phone_numbers_file)

# Loop through the list of target phone numbers
for target_phone_number in target_phone_numbers:
    try:
        # Validate the phone number (optional)
        if not target_phone_number:
            continue

        # Initiate the call
        call = client.calls.create(
            url=url,  # This is where Twilio will send the POST request
            to=target_phone_number,
            from_=twilio_phone_number
        )

        print(f"Call initiated to {target_phone_number}. Call SID: {call.sid}")

        # Optional: Add a delay between calls to avoid rate-limiting or overlapping calls
        time.sleep(15)  # Wait for 15 seconds before making the next call

    except Exception as e:
        print(f"Error initiating call to {target_phone_number}: {e}")
