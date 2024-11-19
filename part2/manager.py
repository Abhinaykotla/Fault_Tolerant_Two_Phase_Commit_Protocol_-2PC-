import socket
import threading


def handle_client(client_socket, client_id, responses, timeout):
    """
    Handles communication with a single participant.
    Sends 'prepare' and waits for the response within a specified timeout.
    """
    try:
        # Send 'prepare' message to the participant
        client_socket.sendall(b"prepare")
        print(f"[Manager] Sent 'prepare' to Participant {client_id}")

        # Set timeout for response
        client_socket.settimeout(timeout)

        # Wait for response
        response = client_socket.recv(1024).decode()
        print(f"[Manager] Received '{response}' from Participant {client_id}")
        responses[client_id] = response
    except socket.timeout:
        # Handle timeout if participant does not respond in time
        print(f"[Manager] Timeout waiting for response from Participant {client_id}. Assuming 'no'.")
        responses[client_id] = "no"
    except Exception as e:
        # Handle other communication errors
        print(f"[Manager] Error communicating with Participant {client_id}: {e}")
        responses[client_id] = "no"
    finally:
        # Remove timeout for any further operations
        client_socket.settimeout(None)


def transaction_coordinator():
    """
    Manager implementation of the 2PC protocol for Part 2.
    Aborts the transaction if any participant times out or responds with 'no'.
    """
    host = "127.0.0.1"
    port = 5000
    timeout = 10  # Timeout for waiting for participant responses
    responses = {}

    # Initialize the server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(2)  # Listen for two participants

    print("[Manager] Waiting for participants to connect...")
    participants = []

    # Accept connections from participants
    for i in range(2):  # Adjust the range for more participants
        client_socket, addr = server.accept()
        print(f"[Manager] Participant {i + 1} connected from {addr}")
        participants.append((client_socket, i + 1))

    # Create and start threads for handling participants
    threads = []
    for client_socket, client_id in participants:
        thread = threading.Thread(target=handle_client, args=(client_socket, client_id, responses, timeout))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Determine transaction outcome based on participant responses
    if all(responses.get(i) == "yes" for i in range(1, 3)):
        print("[Manager] All participants agreed. Committing transaction.")
        decision = "commit"
    else:
        print("[Manager] At least one participant disagreed or did not respond. Aborting transaction.")
        decision = "abort"

    # Send the final decision to all participants
    for client_socket, client_id in participants:
        try:
            print(f"[Manager] Sending final decision '{decision}' to Participant {client_id}")
            client_socket.sendall(decision.encode())
            print(f"[Manager] Final decision '{decision}' sent to Participant {client_id}")
        except Exception as e:
            print(f"[Manager] Failed to send decision to Participant {client_id}: {e}")
        finally:
            # Ensure the socket is closed after sending the decision
            try:
                client_socket.close()
            except Exception as e:
                print(f"[Manager] Error closing socket for Participant {client_id}: {e}")

    # Close the server socket
    server.close()


if __name__ == "__main__":
    transaction_coordinator()
