import socket
import json
import threading
import os

LOG_FILE = "transaction_log_part4.json"


class TransactionManager:
    """
    Transaction Manager implementation for Part 4 of the 2PC protocol.
    Handles persistent logging, client communication, and recovery.
    """

    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.server = None
        self.log = self.load_log()
        self.lock = threading.Lock()

    def load_log(self):
        """
        Load the transaction log from the file or initialize a new one if it doesn't exist.
        """
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as file:
                log = json.load(file)
            # Ensure required keys are present
            log.setdefault("clients", {})
            log.setdefault("decision", None)
            return log
        else:
            return {"clients": {}, "decision": None}

    def save_log(self):
        """
        Save the current state of the transaction log to file.
        """
        with self.lock:
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
        Record the final decision (commit or abort) in the transaction log.
        """
        self.log["decision"] = decision
        self.save_log()

    def handle_client(self, client_socket, client_id):
        """
        Manage communication with a single client during the prepare phase.
        """
        try:
            # Send 'prepare' message to the client
            client_socket.sendall(b"prepare")
            print(f"[Manager] Sent 'prepare' to Client {client_id}")

            # Receive response from the client
            response = client_socket.recv(1024).decode()
            print(f"[Manager] Received '{response}' from Client {client_id}")
            if response == "yes":
                self.log_client_status(client_id, "prepared")
            else:
                self.log_client_status(client_id, "aborted")
        except Exception as e:
            print(f"[Manager] Error communicating with Client {client_id}: {e}")
            self.log_client_status(client_id, "aborted")
        finally:
            client_socket.close()

    def send_decision_to_clients(self):
        """
        Send the final decision (commit/abort) to all clients based on the transaction log.
        """
        print("[Manager] Sending final decision to clients...")
        for client_id, status in self.log["clients"].items():
            if "sent" not in status:
                try:
                    # Wait for the client to reconnect
                    client_socket, addr = self.server.accept()
                    print(f"[Manager] Reconnected with Client at {addr}")
                    client_socket.sendall(self.log["decision"].encode())
                    print(f"[Manager] Sent '{self.log['decision']}' to Client {client_id}")
                    self.log_client_status(client_id, f"{self.log['decision']}_sent")
                    client_socket.close()
                except Exception as e:
                    print(f"[Manager] Error sending decision to Client {client_id}: {e}")

    def transaction_coordinator(self):
        """
        Main transaction coordination process for 2PC.
        Handles the prepare phase and recovery after a manager crash.
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)

        print("[Manager] Waiting for clients to connect...")
        client_threads = []

        # Only accept new clients if not recovering
        if not self.log["clients"]:
            for i in range(2):  # Adjust for more clients if needed
                client_socket, addr = self.server.accept()
                print(f"[Manager] Client {i + 1} connected from {addr}")
                self.log_client_status(f"{addr[0]}:{addr[1]}", "connected")
                thread = threading.Thread(target=self.handle_client, args=(client_socket, f"{addr[0]}:{addr[1]}"))
                client_threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in client_threads:
                thread.join()

            # Decide to commit or abort based on client responses
            if all(status == "prepared" for status in self.log["clients"].values()):
                print("[Manager] All clients agreed. Committing transaction.")
                self.log_decision("commit")
            else:
                print("[Manager] At least one client disagreed. Aborting transaction.")
                self.log_decision("abort")

        # Send the decision to reconnecting clients
        self.send_decision_to_clients()
        self.server.close()
        print("[Manager] Transaction completed.")


if __name__ == "__main__":
    manager = TransactionManager()
    manager.transaction_coordinator()
