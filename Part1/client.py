import socket
import sys


def participant(participant_id):
    """
    Participant process in the 2PC protocol. Handles 'prepare' messages 
    and waits for the final decision while respecting timeouts.
    """
    host = "127.0.0.1"
    port = 5000

    # Establish a connection with the manager
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        print(f"[Participant {participant_id}] Connected to Manager.")

        aborted = False  # Tracks if the participant has aborted

        # Wait for the 'prepare' message with a timeout
        client_socket.settimeout(5)
        print(f"[Participant {participant_id}] Waiting for 'prepare' message...")
        
        try:
            message = client_socket.recv(1024).decode()
            if message == "prepare":
                if not aborted:
                    print(f"[Participant {participant_id}] Received 'prepare' message.")
                    # Send "yes" response to the manager
                    response = "yes"
                    client_socket.sendall(response.encode())
                    print(f"[Participant {participant_id}] Sent response: {response}")
                else:
                    print(f"[Participant {participant_id}] Ignoring delayed 'prepare' message.")
            else:
                print(f"[Participant {participant_id}] Unexpected message: {message}")
        except socket.timeout:
            # Abort transaction if 'prepare' is not received within the timeout
            print(f"[Participant {participant_id}] Timeout waiting for 'prepare'. Aborting transaction.")
            aborted = True
            client_socket.sendall(b"no")

        # Wait for the final decision ('commit' or 'abort') with an extended timeout
        client_socket.settimeout(15)
        while True:
            try:
                decision = client_socket.recv(1024).decode()
                if decision in ["commit", "abort"]:
                    print(f"[Participant {participant_id}] Final decision received: {decision}")
                    break
                else:
                    print(f"[Participant {participant_id}] Ignored unexpected message: {decision}")
            except socket.timeout:
                print(f"[Participant {participant_id}] Timeout waiting for final decision.")
                break 
            except Exception as e:
                print(f"[Participant {participant_id}] Error waiting for final decision: {e}")
                break 

    except Exception as e:
        print(f"[Participant {participant_id}] Error connecting to Manager: {e}")

    finally:
        # Close the connection to the manager
        client_socket.close()
        print(f"[Participant {participant_id}] Connection closed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py <participant_id>")
        sys.exit(1)

    participant_id = int(sys.argv[1])
    participant(participant_id)
