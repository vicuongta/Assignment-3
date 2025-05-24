### Blockchain Manual
Run the program by the command:
    python3 peer.py [HOST_NAME] [HOST_PORT] [MY_PORT]
where:
- [HOST_NAME] is the well-known peer such as silicon, hawk, eagle, then .cs.umanitoba.ca
- [HOST_NAME] is the port number of the well-known peer
- [MY_PORT] is the port the peer is running on
Example use: 
    python3 peer.py silicon.cs.umanitoba.ca 8999 8822

* Note on my peer:
1. It takes around 2-5 minutes to synchronize and my peer will send 'Peers with longest chain', 'Initializing chain...', and 'Chain length' to show that it starts doing concensus. I have commented time.sleep(2) to track (line 123 & 129)
2. My concensus starts when my peer receives stats from at least 4 peers (line 115 - 208).
   - When received the length of the chain, my peer would create a list that stores empty block and request 50 blocks at a time from selected peers using round-robin.
    - The while loop from line 158 - 163 would search for empty blocks (None) in my chain and request those blocks to peers. Upon receving blocks, it adds the block to the chain as a Block object.
    - I clean up peers when get keyboard interupt (close method line 319 - 326).
3. My peer only send STATS and GET_BLOCK_REPLY if it is valid, that is it has received all the blocks and the chain is valid.
4. While fetching blocks using round-robin, not all peers in my tracking list will reply so it would sometimes print out 1 peer sending GET_BLOCK_REPLY but the block height is not continuous, showing that I don't send all blocks to just 1 peer. Also, there might be a situation where 1 peer has longer chain than the majority, my peer would take that peer and start requesting blocks. I believe that's the only case where I request blocks from just 1 peer.
   
* Note when testing before submission
Some peers send data when their chain is not full so I got into a case where 2 peers send STATS_REPLY for chains of length 0 and 1 so my peer starts concensus with that problem. If the well-known peers don't send correct STATS, my peer would just do concensus on those incorrect length. I have an if statement to do concensus every 1 minute so I guess it would re-do concensus with the correct length.
