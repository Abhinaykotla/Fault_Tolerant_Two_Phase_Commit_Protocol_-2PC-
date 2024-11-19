import socket
import sys
import time


def participant(participant_id):
    """
    Participant process for Part 3 of the 2PC protocol.
    Handles 'prepare' messages and waits for the manager to recover in case of a crash,
    retrying connections until the final decision is received.
    """
    host = "127.0.0.1"
    port = 5000
    decision_received = False

    while not decision_received:
        try:
            # Attempt to connect to the manager
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            print(f"[Participant {participant_id}] Connected to Manager.")

            try:
                # Wait for either 'prepare' or final decision
                message = client_socket.recv(1024).decode()
                if message == "prepare":
                    print(f"[Participant {participant_id}] Received 'prepare' message.")
                    response = "yes"  # Simulated positive response
                    client_socket.sendall(response.encode())
                    print(f"[Participant {participant_id}] Sent response: {response}")
                elif message in ["commit", "abort"]:
                    print(f"[Participant {participant_id}] Final decision received: {message}")
                    decision_received = True  # Exit loop after receiving the decision
            except socket.timeout:
                print(f"[Participant {participant_id}] Timeout waiting for messages.")
        except ConnectionRefusedError:
            # Retry connection if the manager is unavailable
            print(f"[Participant {participant_id}] Manager not available. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"[Participant {participant_id}] Error: {e}")
        finally:
            # Ensure the connection is closed
            client_socket.close()
            print(f"[Participant {participant_id}] Connection closed.")

    print(f"[Participant {participant_id}] Transaction complete. Final decision: {message}")


if __name__ == "__main__":
    # Ensure the script is called with the correct arguments
    if len(sys.argv) != 2:
        print("Usage: python client.py <participant_id>")
        sys.exit(1)

    participant_id = int(sys.argv[1])
    participant(participant_id)
