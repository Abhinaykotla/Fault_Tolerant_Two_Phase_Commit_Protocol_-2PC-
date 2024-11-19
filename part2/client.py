import socket
import sys
import time


def participant(participant_id, response_behavior="yes"):
    """
    Participant process for Part 2 of the 2PC protocol.
    Handles 'prepare' messages and simulates responses based on the specified behavior.
    """
    host = "127.0.0.1"
    port = 5000

    # Connect to the manager
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((host, port))
        print(f"[Participant {participant_id}] Connected to Manager.")

        # Wait for the 'prepare' message
        message = client_socket.recv(1024).decode()
        if message == "prepare":
            print(f"[Participant {participant_id}] Received 'prepare' message.")
            if response_behavior == "yes":
                # Respond with "yes"
                client_socket.sendall(b"yes")
                print(f"[Participant {participant_id}] Sent response: yes")
            elif response_behavior == "no":
                # Respond with "no"
                client_socket.sendall(b"no")
                print(f"[Participant {participant_id}] Sent response: no")
            elif response_behavior == "timeout":
                # Simulate a timeout by not responding
                print(f"[Participant {participant_id}] Simulating timeout. No response sent.")
                time.sleep(20)  # Stall longer than the manager's timeout period
        else:
            print(f"[Participant {participant_id}] Unexpected message: {message}")

        # Wait for the final decision ('commit' or 'abort') from the manager
        try:
            decision = client_socket.recv(1024).decode()
            if decision in ["commit", "abort"]:
                print(f"[Participant {participant_id}] Final decision received: {decision}")
            else:
                print(f"[Participant {participant_id}] Unexpected message: {decision}")
        except socket.timeout:
            print(f"[Participant {participant_id}] Timeout waiting for final decision.")

    except Exception as e:
        print(f"[Participant {participant_id}] Error communicating with Manager: {e}")

    finally:
        # Close the connection to the manager
        client_socket.close()
        print(f"[Participant {participant_id}] Connection closed.")


if __name__ == "__main__":
    # Ensure correct usage with required arguments
    if len(sys.argv) != 3:
        print("Usage: python client.py <participant_id> <response_behavior>")
        print("response_behavior: yes (default), no, or timeout")
        sys.exit(1)

    participant_id = int(sys.argv[1])
    response_behavior = sys.argv[2]
    participant(participant_id, response_behavior)
