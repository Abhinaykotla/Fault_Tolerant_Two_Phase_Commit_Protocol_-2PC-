import socket
import time
import threading


def handle_client(client_socket, client_id, responses):
    """
    Handles communication with a single participant during the 2PC protocol.
    Sends 'prepare' and records the participant's response.
    """
    try:
        # Send 'prepare' message to the participant
        client_socket.sendall(b"prepare")
        print(f"[Manager] Sent 'prepare' to Participant {client_id}")

        # Receive participant's response
        response = client_socket.recv(1024).decode()
        print(f"[Manager] Received '{response}' from Participant {client_id}")
        responses[client_id] = response
    except socket.timeout:
        print(f"[Manager] Timeout waiting for response from Participant {client_id}. Assuming 'no'.")
        responses[client_id] = "no"  # Default to 'no' if timeout occurs
    except Exception as e:
        print(f"[Manager] Error communicating with Participant {client_id}: {e}")
        responses[client_id] = "no"  # Default to 'no' on error
    finally:
        client_socket.settimeout(None)  # Disable timeout for subsequent operations


def transaction_coordinator():
    """
    Transaction manager for the 2PC protocol.
    Simulates a delay before sending 'prepare' to participants.
    """
    host = "127.0.0.1"
    port = 5000
    responses = {}

    # Setup server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(2)  # Listening for two participants

    print("[Manager] Waiting for participants to connect...")
    participants = []

    # Accept connections from participants
    for i in range(2):
        client_socket, addr = server.accept()
        client_socket.settimeout(10)  # Timeout for receiving messages
        print(f"[Manager] Participant {i + 1} connected from {addr}")
        participants.append((client_socket, i + 1))

    # Simulate a delay before sending 'prepare' to participants
    print("[Manager] Simulating failure...")
    time.sleep(10)

    # Start threads to handle participants
    threads = []
    for client_socket, client_id in participants:
        thread = threading.Thread(target=handle_client, args=(client_socket, client_id, responses))
        threads.append(thread)
        thread.start()

    # Wait for all participant threads to complete
    for thread in threads:
        thread.join()

    # Determine the transaction decision based on participant responses
    if all(responses.get(i) == "yes" for i in range(1, 3)):
        print("[Manager] All participants agreed. Committing transaction.")
        decision = "commit"
    else:
        print("[Manager] At least one participant disagreed. Aborting transaction.")
        decision = "abort"

    # Notify participants of the final decision
    for client_socket, client_id in participants:
        try:
            print(f"[Manager] Sending final decision '{decision}' to Participant {client_id}")
            client_socket.sendall(decision.encode())
            print(f"[Manager] Final decision '{decision}' sent to Participant {client_id}")
        except Exception as e:
            print(f"[Manager] Failed to send decision to Participant {client_id}: {e}")
        finally:
            try:
                client_socket.close()
            except Exception as e:
                print(f"[Manager] Error closing socket for Participant {client_id}: {e}")

    # Close the server socket
    server.close()


if __name__ == "__main__":
    transaction_coordinator()
