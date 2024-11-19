
# Distributed Systems Project
## Fault-Tolerant Two-Phase Commit Protocol (2PC)

This project demonstrates a distributed fault-tolerant **2-phase commit (2PC) protocol** with failure simulations, covering multiple parts of the protocol.

---

## Setup and Dependencies

**Requirements**:
- Python 3.8 or higher
- Basic understanding of sockets and multithreading in Python

**Installation**:
No external dependencies are required. The built-in `socket` and `threading` modules are used.

---

## Project Structure

The project is divided into folders for each part:

## How to Run the Programs

### Part 1

1. Navigate to the `part1` folder.
   ```
   cd part1
   ```

2. Start the **manager** (transaction coordinator):
   ```bash
   python manager.py
   ```

3. Start **participants** (in separate terminals):
   ```
   python client.py 1
   ```

   ```
   python client.py 2
   ```

4. Observe the output:
   - The manager simulates a delay before sending "prepare."
   - Participants timeout waiting for "prepare," transition to `abort`, and still wait for the final decision (`commit` or `abort`).

---

### Part 2

1. Navigate to the `part2` folder.
   ```
   cd part2
   ```

2. Start the **manager** (transaction coordinator):
   ```
   python manager.py
   ```

3. Start **participants** (in separate terminals):
   - **Participant 1** responds with "yes":
     ```
     python client.py 1 yes
     ```
   - **Participant 2** simulates a timeout:
     ```
     python client.py 2 timeout
     ```

4. Observe the output:
   - The manager aborts the transaction upon receiving a timeout from Participant 2.

---

### Part 3

1. Navigate to the `part3` folder.
   ```
   cd part3
   ```

2. Make sure there is no existing log from the last run. Start the **manager** (transaction coordinator):
   ```
   python manager.py
   ```

3. Start **participants** (in separate terminals):
   - **Participant 1** responds with "yes":
     ```
     python client.py 1
     ```
   - **Participant 2** simulates a timeout:
     ```
     python client.py 2
     ```

4. After the crash restart the manager:
   ```
   python manager.py
   ```

5. Observe the output:
   - The manager will recover the transaction and commit it.

---

### Part 4

1. Navigate to the `part4` folder.
   ```
   cd part4
   ```

2. Make sure there is no existing log from the last run. Start the **manager** (transaction coordinator):
   ```
   python manager.py
   ```

3. Start **participants** (in separate terminals):
   - **Participant 1** responds with "yes":
     ```
     python client.py 1
     ```
   - **Participant 2** simulates a timeout:
     ```
     python client.py 2
     ```

4. After the **crash** restart the client:
   ```
   python client.py 1
   ```

5. Observe the output:
   - The client will recover the transaction and connects back to the manager.

---