# 🧱 Blockchain Peer Network Manual

## 📌 Running the Program on Terminal with connection to UoM aviary

To start a peer in the blockchain network, use the following command:

```bash
python3 peer.py [HOST_NAME] [HOST_PORT] [MY_PORT]
```

### 🔧 Parameters:
- `HOST_NAME`: The hostname of a known peer (e.g., `silicon`, `hawk`, `eagle`, followed by `.cs.umanitoba.ca`)
- `HOST_PORT`: The port number of the known peer
- `MY_PORT`: The port number you want your peer to run on

### ▶️ Example:
```bash
python3 peer.py silicon.cs.umanitoba.ca 8999 8822
```

---

## 📝 Peer Behavior Overview

### ⏳ 1. Initialization
- Takes **2–5 minutes** to sync.
- Displays messages like:
  - `'Peers with longest chain'`
  - `'Initializing chain...'`
  - `'Chain length'`

> `time.sleep(2)` is used to track sync progress (see lines 123 & 129 in the code).

---

### 🤝 2. Consensus Mechanism
Consensus starts when stats are received from at least **4 peers** (lines 115–208).

#### 🔄 Round-Robin Fetching:
- Peer checks the length of the chain from each peer.
- Builds a list of `None`/empty blocks.
- Requests **50 blocks at a time** from peers using **round-robin**.

#### 🔍 Block Retrieval Loop:
- Between **lines 158–163**, the peer:
  - Searches for missing (`None`) blocks.
  - Sends block requests to peers.
  - Adds received blocks as `Block` objects to its chain.

#### 🧹 Cleanup:
- Peer disconnects and cleans up on keyboard interrupt (lines 319–326).

---

### 📨 3. Message Types Sent
- Only sends:
  - `STATS`
  - `GET_BLOCK_REPLY` (if valid and complete)

---

### 🧠 4. Peer Response Issues
- Not all peers may respond during round-robin, causing:
  - Gaps in received blocks.
  - Non-continuous chains.
- If a peer has a longer valid chain than others, it will prioritize that one for fetching.

---

## ⚠️ Notes on Testing and Edge Cases

- **Initial State Issues**: If peers reply with `STATS_REPLY` for chains of length 0 or 1, consensus may start incorrectly.
- **Workaround**: Added logic to **re-do consensus every 1 minute**, ensuring the peer eventually syncs to the correct chain length.
- Recommend using **well-known peers** for accurate stats during testing.

---
