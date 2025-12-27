import time
import asyncio
import os
from datetime import datetime
from telethon.sync import TelegramClient
from telethon import errors
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TelegramForwarder:
    def __init__(self, api_id, api_hash, phone_number):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.client = TelegramClient('session_' + phone_number, api_id, api_hash)

    async def authenticate(self):
        """Handle authentication with session persistence"""
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            working_mode = os.getenv('WORKING_MODE', 'interactive')
            
            if working_mode == 'process':
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] -> Authentication required but running in process mode")
                print("Please run once in interactive mode to authenticate, then switch to process mode")
                return False
            
            await self.client.send_code_request(self.phone_number)
            try:
                await self.client.sign_in(self.phone_number, input('Enter the code: '))
            except errors.rpcerrorlist.SessionPasswordNeededError:
                password = input('Two-step verification is enabled. Enter your password: ')
                await self.client.sign_in(password=password)
        
        return True

    async def list_chats(self):
        if not await self.authenticate():
            return
            
        # Get a list of all the dialogs (chats)
        dialogs = await self.client.get_dialogs()
        chats_file = open(f"chats_of_{self.phone_number}.txt", "w", encoding="utf-8")
        # Print information about each chat
        for dialog in dialogs:
            print(f"Chat ID: {dialog.id}, Title: {dialog.title}")
            chats_file.write(f"Chat ID: {dialog.id}, Title: {dialog.title} \n")
          

        print("List of groups printed successfully!")

    async def forward_messages_to_channel(self, source_chat_ids, destination_channel_id, keywords):
        if not await self.authenticate():
            return

        try:
            # First, populate the entity cache by getting dialogs
            await self.client.get_dialogs()
            
            # Get destination entity first to populate cache
            dest_entity = await self.client.get_entity(destination_channel_id)
            
            # Get source entities and destination entity
            source_entities = []
            source_inputs = []
            last_message_ids = {}
            
            for source_id in source_chat_ids:
                source_entity = await self.client.get_entity(source_id)
                source_input = await self.client.get_input_entity(source_entity)
                source_entities.append(source_entity)
                source_inputs.append(source_input)
                
                # Get the last message ID for each source
                messages = await self.client.get_messages(source_input, limit=1)
                last_message_ids[source_id] = messages[0].id if messages else 0
            
        except ValueError as e:
            print(f"Error resolving chat entities: {e}")
            print("Make sure the chat IDs are correct and you have access to all chats")
            return
        except Exception as e:
            print(f"Error accessing chats: {e}")
            return

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] -> Listening for new messages from {len(source_chat_ids)} sources")
        
        while True:
            # Check each source chat for new messages
            for i, (source_id, source_input) in enumerate(zip(source_chat_ids, source_inputs)):
                messages = await self.client.get_messages(source_input, min_id=last_message_ids[source_id], limit=None)

                for message in reversed(messages):
                    if message.text:
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        source_name = getattr(source_entities[i], 'title', None) or getattr(source_entities[i], 'first_name', f"Chat {source_id}")
                        print(f"[{timestamp}] -> Message received from '{source_name}': {message.text[:50]}{'...' if len(message.text) > 50 else ''}")
                        
                        # Check if the message text includes any of the keywords
                        if keywords and keywords != ['']:
                            matched_keyword = None
                            for keyword in keywords:
                                if keyword.strip() and keyword.strip().lower() in message.text.lower():
                                    matched_keyword = keyword.strip()
                                    break
                            
                            if matched_keyword:
                                print(f"[{timestamp}] -> Matches with keywords? True (matched: '{matched_keyword}')")
                                try:
                                    await self.client.send_message(destination_channel_id, message.text)
                                    print(f"[{timestamp}] -> Message forwarded")
                                except Exception as e:
                                    print(f"[{timestamp}] -> Error forwarding message: {e}")
                            else:
                                print(f"[{timestamp}] -> Matches with keywords? False")
                        else:
                            print(f"[{timestamp}] -> Matches with keywords? N/A (forwarding all messages)")
                            try:
                                await self.client.send_message(destination_channel_id, message.text)
                                print(f"[{timestamp}] -> Message forwarded")
                            except Exception as e:
                                print(f"[{timestamp}] -> Error forwarding message: {e}")

                    # Update the last message ID for this source
                    last_message_ids[source_id] = max(last_message_ids[source_id], message.id)

            # Add a delay before checking for new messages again
            await asyncio.sleep(5)  # Adjust the delay time as needed


# Function to read credentials from environment or file
def read_credentials():
    # Try environment variables first
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    phone_number = os.getenv('PHONE_NUMBER')
    
    if api_id and api_hash and phone_number:
        return api_id, api_hash, phone_number
    
    # Fallback to file
    try:
        with open("credentials.txt", "r") as file:
            lines = file.readlines()
            api_id = lines[0].strip()
            api_hash = lines[1].strip()
            phone_number = lines[2].strip()
            return api_id, api_hash, phone_number
    except FileNotFoundError:
        print("Credentials not found in environment or file.")
        return None, None, None

# Function to write credentials to file
def write_credentials(api_id, api_hash, phone_number):
    with open("credentials.txt", "w") as file:
        file.write(api_id + "\n")
        file.write(api_hash + "\n")
        file.write(phone_number + "\n")

async def main():
    working_mode = os.getenv('WORKING_MODE', 'interactive')
    
    # Attempt to read credentials
    api_id, api_hash, phone_number = read_credentials()

    # If credentials not found, prompt the user to input them (interactive mode only)
    if api_id is None or api_hash is None or phone_number is None:
        if working_mode == 'process':
            print("Error: Credentials not found in environment variables")
            return
        
        api_id = input("Enter your API ID: ")
        api_hash = input("Enter your API Hash: ")
        phone_number = input("Enter your phone number: ")
        # Write credentials to file for future use
        write_credentials(api_id, api_hash, phone_number)

    forwarder = TelegramForwarder(api_id, api_hash, phone_number)
    
    if working_mode == 'process':
        # Process mode - read from environment variables
        source_ids_str = os.getenv('LIST_OF_SOURCE_IDS')
        destination_id_str = os.getenv('DESTINATION_ID')
        keywords_str = os.getenv('KEYWORDS', '')
        
        if not source_ids_str or not destination_id_str:
            print("Error: LIST_OF_SOURCE_IDS and DESTINATION_ID must be set in environment")
            return
        
        source_chat_ids = [int(id.strip()) for id in source_ids_str.split(',')]
        destination_channel_id = int(destination_id_str)
        keywords = [k.strip() for k in keywords_str.split(',') if k.strip()] if keywords_str else []
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] -> Starting in process mode")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] -> Sources: {source_chat_ids}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] -> Destination: {destination_channel_id}")
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] -> Keywords: {keywords}")
        
        await forwarder.forward_messages_to_channel(source_chat_ids, destination_channel_id, keywords)
    else:
        # Interactive mode
        print("Choose an option:")
        print("1. List Chats")
        print("2. Forward Messages")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            await forwarder.list_chats()
        elif choice == "2":
            source_chat_ids_input = input("Enter the source chat IDs (comma separated): ")
            source_chat_ids = [int(id.strip()) for id in source_chat_ids_input.split(",")]
            destination_channel_id = int(input("Enter the destination chat ID: "))
            print("Enter keywords if you want to forward messages with specific keywords, or leave blank to forward every message!")
            keywords = input("Put keywords (comma separated if multiple, or leave blank): ").split(",")
            
            await forwarder.forward_messages_to_channel(source_chat_ids, destination_channel_id, keywords)
        else:
            print("Invalid choice")

# Start the event loop and run the main function
if __name__ == "__main__":
    asyncio.run(main())
