import socket
import sys
import time
import json
import os

LOG_FILE_TEMPLATE = "client_{participant_id}_log.json"


class Participant:
    """
    Participant implementation for the 2PC protocol.
    Handles state persistence, communication with the manager, and recovery after failure.
    """

    def __init__(self, participant_id, host="127.0.0.1", port=5000):
        self.participant_id = participant_id
        self.host = host
        self.port = port
        self.log_file = LOG_FILE_TEMPLATE.format(participant_id=participant_id)
        self.transaction_log = self.load_log()

    def load_log(self):
        """
        Load the transaction state from a log file or initialize a new log.
        """
        if os.path.exists(self.log_file):
            with open(self.log_file, "r") as file:
                return json.load(file)
        return {"state": None}

    def save_log(self):
        """
        Save the current transaction state to the log file.
        """
        with open(self.log_file, "w") as file:
            json.dump(self.transaction_log, file)

    def set_state(self, state):
        """
        Update and persist the transaction state in the log.
        """
        self.transaction_log["state"] = state
        self.save_log()

    def communicate_with_manager(self):
        """
        Handles communication with the manager, including recovery and fetching decisions.
        """
        while True:
            try:
                # Establish connection to the manager
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((self.host, self.port))
                print(f"[Participant {self.participant_id}] Connected to Manager.")

                # Recovery logic if the participant has already prepared
                if self.transaction_log["state"] == "prepared":
                    print(f"[Participant {self.participant_id}] Fetching final decision after recovery.")
                    decision = client_socket.recv(1024).decode()
                    if decision in ["commit", "abort"]:
                        print(f"[Participant {self.participant_id}] Final decision received: {decision}")
                        self.set_state(decision)
                        break
                    else:
                        print(f"[Participant {self.participant_id}] Unexpected message during recovery: {decision}")
                        continue

                # Handle 'prepare' message from the manager
                message = client_socket.recv(1024).decode()
                if message == "prepare":
                    print(f"[Participant {self.participant_id}] Received 'prepare' message.")
                    self.set_state("prepared")  # Update state to 'prepared'
                    response = "yes"
                    client_socket.sendall(response.encode())
                    print(f"[Participant {self.participant_id}] Sent response: {response}")

                    # Simulate failure for Participant 1
                    if self.participant_id == 1:
                        print(f"[Participant {self.participant_id}] Simulating failure...")
                        time.sleep(5)  # Simulate crash delay
                        print(f"[Participant {self.participant_id}] Exiting due to simulated crash.")
                        return  # Exit to simulate a crash

                    # Wait for the final decision
                    decision = client_socket.recv(1024).decode()
                    if decision in ["commit", "abort"]:
                        print(f"[Participant {self.participant_id}] Final decision received: {decision}")
                        self.set_state(decision)
                        break
                else:
                    print(f"[Participant {self.participant_id}] Unexpected message: {message}")

            except ConnectionRefusedError:
                # Retry logic if the manager is unavailable
                print(f"[Participant {self.participant_id}] Manager not available. Retrying...")
                time.sleep(5)
            except Exception as e:
                print(f"[Participant {self.participant_id}] Error: {e}")
                break
            finally:
                # Ensure the socket is closed after communication
                client_socket.close()
                print(f"[Participant {self.participant_id}] Connection closed.")

        print(f"[Participant {self.participant_id}] Transaction complete. Final state: {self.transaction_log['state']}")


if __name__ == "__main__":
    # Validate command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python client.py <participant_id>")
        sys.exit(1)

    participant_id = int(sys.argv[1])
    participant = Participant(participant_id)
    participant.communicate_with_manager()
