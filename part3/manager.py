import socket
import json
import os
import sys


LOG_FILE = "transaction_log.json"


class TransactionManager:
    def __init__(self, host="127.0.0.1", port=5000):
        """
        Initialize the TransactionManager with a host, port, and transaction log.
        """
        self.host = host
        self.port = port
        self.server = None
        self.log = self.load_log()

    def load_log(self):
        """
        Load the transaction log from file or initialize a new one if it doesn't exist.
        """
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as file:
                log = json.load(file)
            # Ensure required keys are present in the log
            if "clients" not in log:
                log["clients"] = {}
            if "decision" not in log:
                log["decision"] = None
            return log
        else:
            # Create a new log if no file exists
            return {"clients": {}, "decision": None}

    def save_log(self):
        """
        Save the current transaction log to file.
        """
        with open(LOG_FILE, "w") as file:
            json.dump(self.log, file)

    def log_client_status(self, client_id, status):
        """
        Update the status of a client in the transaction log.
        """
        self.log["clients"][client_id] = status
        self.save_log()

    def log_decision(self, decision):
        """
        Record the final transaction decision in the log.
        """
        self.log["decision"] = decision
        self.save_log()

    def recover_and_continue(self):
        """
        Recover from a simulated crash and finish sending the decision to remaining clients.
        """
        print("[Manager] Recovering from crash...")

        # Verify the decision is available for recovery
        if not self.log["decision"]:
            print("[Manager] Error: Decision is missing from the log. Recovery cannot proceed.")
            return

        # Identify clients that haven't received the decision
        remaining_clients = [
            client_id
            for client_id, status in self.log["clients"].items()
            if "sent" not in status
        ]

        print(f"[Manager] Waiting for {len(remaining_clients)} clients to reconnect...")

        # Wait for remaining clients to reconnect
        reconnected_clients = {}
        for client_id in remaining_clients:
            client_socket, addr = self.server.accept()
            print(f"[Manager] Reconnected with Client at {addr}")
            reconnected_clients[client_id] = client_socket

        # Send the decision to reconnected clients
        for client_id, client_socket in reconnected_clients.items():
            try:
                client_socket.sendall(self.log["decision"].encode())
                print(f"[Manager] Sent '{self.log['decision']}' to {client_id}")
                self.log_client_status(client_id, f"{self.log['decision']}_sent")
            except Exception as e:
                print(f"[Manager] Error sending decision to {client_id}: {e}")
            finally:
                client_socket.close()

        print("[Manager] Transaction recovery complete.")

    def transaction_coordinator(self):
        """
        Coordinate the two-phase commit (2PC) protocol.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

        # Begin transaction coordination
        if not self.log["clients"]:  # Accept new connections if not recovering
            print("[Manager] Waiting for clients to connect...")
            for i in range(2):  # Adjust this range for more clients
                client_socket, addr = self.server.accept()
                print(f"[Manager] Client {i + 1} connected from {addr}")
                self.log_client_status(f"{addr[0]}:{addr[1]}", "connected")
            print("[Manager] All clients connected.")

            # Simulate the prepare phase
            for client_id in list(self.log["clients"].keys()):
                self.log_client_status(client_id, "prepared")

            # Make a decision
            self.log_decision("commit")

            # Send the decision to the first client
            first_client = list(self.log["clients"].keys())[0]
            first_client_socket, addr = self.server.accept()
            try:
                first_client_socket.sendall(self.log["decision"].encode())
                print(f"[Manager] Sent '{self.log['decision']}' to {first_client}")
                self.log_client_status(first_client, f"{self.log['decision']}_sent")
            except Exception as e:
                print(f"[Manager] Error sending decision to {first_client}: {e}")
            finally:
                first_client_socket.close()

            # Simulate a crash after sending to one client
            print("[Manager] Simulating crash after sending decision to one client.")
            sys.exit(0)

        # Recovery process
        self.recover_and_continue()

        self.server.close()


if __name__ == "__main__":
    manager = TransactionManager()
    manager.transaction_coordinator()
