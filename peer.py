import socket
import sys
import uuid
import json
import time
import hashlib
import random
from block import Block

BUFFER_SIZE = 1024
CHAIN_HOST = sys.argv[1] # silicon.cs.umanitoba.ca
CHAIN_PORT = int(sys.argv[2]) # 8999
PEER_PORT = int(sys.argv[3]) # 8822
USERNAME = "Cuong Ta"
DIFFICULTY = 8
MAX_MSG = 10
MAX_PEERS = 3
INTERVAL = 60
SILLY_GOOSE = '130.179.28.116'
BLOCK_RANGE = 50
WAIT_BLOCK = 5

class Peer:
    def __init__(self, chain_host, chain_port):
        # Initialize the Peer with a UDP socket and connect to silicon
        self.chain_host = chain_host
        self.chain_port = chain_port
        print("Creating UDP socket\n")
        try:
            self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP socket
            self.peer_socket.bind(("", PEER_PORT))
            self.peer_socket.settimeout(5)
            self.ip_address = socket.gethostbyname(socket.gethostname())
            # print(f"IP address: {self.ip_address}")
            print(f"Peer connected to {self.chain_host}:{self.chain_port}\n")
        except socket.timeout as e:
            print(f"Socket timeout: {e}")
        # Peer"s items
        self.peer_list = [] # keep track of known peers
        self.peer_name = USERNAME 
        self.stats_data = []
        self.chain = []
    
    def trackPeer(self, peer_data):
        self.peer_list.append(peer_data)
        print(f'Added peer {peer_data["host"], peer_data["port"]} to list!')
        print(f'We\'ve known {len(self.peer_list)} peer(s)!\n')
        
    def sendGossipMessage(self, host, port):
        # Connect to the Chain server and send GOSSIP message
        content = {
            "type": "GOSSIP",
            "host": self.ip_address,
            "port": 8822,
            "id": str(uuid.uuid1()),
            "name": self.peer_name
        }
        try: # send GOSSIP to peer
            json_content = json.dumps(content)
            self.peer_socket.sendto(json_content.encode(), (host, port))
            print(f"GOSSIP {content} sent to peer {host}:{port}\n")
            return content
        except json.JSONDecodeError as e:
            print("Failed to decode JSON in function:", e) 
        except Exception as e:
            print(f"Error in sending GOSSIP: {e}") 
            
    def sendGossipReply(self, address):
        host, port = address
        content = {
            "type": "GOSSIP_REPLY",
            "host": host,
            "port": port,
            "name": self.peer_name
        }
        json_content = json.dumps(content)
        self.peer_socket.sendto(json_content.encode(), address)
        print(f"Replied to peer {address}")

    def sendStatsMessage(self, host, port):
        # Handle the stats message
        content = {
            "type": "STATS"
        }  
        try:
            json_content = json.dumps(content)
            self.peer_socket.sendto(json_content.encode(), (host, port))
            # print(f"Stats sent to peer {host, port}\n")
            # Continue doing concensus
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)   
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    
    def handleStatsReply(self, reply, address):
        print(f'STATS_REPLY! from {address}')
        print("Chain is height {} with hash {}\n".format(
            reply["height"],
            reply["hash"]
        ))
        if reply["height"] is not None and int(reply["height"]) > 0 and reply["hash"] is not None:
            host, port = address
            stats = {
                "host": host,
                "port": port,
                "height": int(reply["height"]),
            }
            if stats not in self.stats_data:
                self.stats_data.append(stats)
                print(f'Tracking stats from peer {address}!')
                print(f'{len(self.stats_data)} stats collected!\n')
            
            # print(f'Chain? {len(self.chain) > 0}\n')
            if self.stats_data and len(self.stats_data) > 3 and len(self.chain) <= 0: # Collect stats from at least 4 peers to start concensus
                print('HAVE DATA! DOING CONCENSUS...\n')
                self.doConsensus(self.stats_data)

    def doConsensus(self, data):
        # print(f'data: {data}')
        max_height = max(int(stats["height"]) for stats in data)
        max_height_entries = [(stats["host"], stats["port"]) for stats in data if int(stats["height"]) == max_height]
        print(f'Peers with longest chain: {max_height_entries} with length {max_height}\n')
        # time.sleep(2)
        # Intialize chain then request blocks if all entries are None
        if len(self.chain) == 0:
            print(f'Initializing chain...\n')
            self.chain = [None] * max_height
            print(f'Chain length: {len(self.chain)}\n')
            time.sleep(2)
        
        if any(entry is None for entry in self.chain):
            print('Doing concensus...\n')
            self.requestBlock(max_height_entries, BLOCK_RANGE)
        else:
            print(f'Chain is complete! Validating chain...\n')
            time.sleep(2) # pretending it takes some time to validate chain 
            if self.validateBlocksInChain(self.chain):
                print('ALL BLOCKS ARE VALID! VALIDATING CHAIN...\n')
                time.sleep(2)
                if self.validateChain(self.chain):
                    print(f'Chain is valid! I\'m a peer now!!!\n')
                else:
                    print(f'Chain is invalid! Re-doing concensus!\n')
                    self.doConsensus(self.stats_data)
            else:
                print('BLOCKS INVALID! RE-DO CONCENSUS\n')
                self.doConsensus(self.stats_data)
        
    def requestBlock(self, peers, block_chunk):
        try:
            # Create a list of empty entry
            empty_block_list = []
            current_height = 0
            # Return 50 empty blocks
            # If there are less than 50 non-None blocks, iterate through those only.
            # No need to iterate 50 times
            none_count = self.chain.count(None)
            while len(empty_block_list) < min(block_chunk, none_count):
                # print(f'Current height: {current_height}')
                if self.chain[current_height] == None:
                    empty_block_list.append(current_height)
                current_height += 1
            # print(f'empty blocks: {empty_block_list}\n')
            
            current_peer_index = 0
            # Request 50 blocks from peers
            print(f'Requesting {min(block_chunk, none_count)} blocks from peer(s) {peers}\n')
            for index in empty_block_list:
                selected_peer = peers[current_peer_index]
                content = {
                    "type": "GET_BLOCK",
                    "height": index
                }
                json_content = json.dumps(content)
                self.peer_socket.sendto(json_content.encode(), selected_peer)
                current_peer_index = (current_peer_index + 1) % len(peers)
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
        except Exception as e:
            print(f"Error1: {e}")
                    
    def handleGetBlockReply(self, reply, count):
        mined_by = reply.get("minedBy")
        messages = reply.get("messages")
        nonce =  reply.get("nonce")
        timestamp = reply.get("timestamp")
        height = int(reply.get("height"))
        hash = reply.get('hash')
        # update chain with new block
        self.chain[height] = Block(mined_by, messages, nonce, hash, height, timestamp)
        print(f'Added block of height {height} mined by {mined_by} to chain!\n') 
        count += 1
            
    def validateBlocksInChain(self, chain):
        for index in range(len(chain)):
            hash_base = hashlib.sha256()
            if index > 0:
                hash_base.update(chain[index-1].getHash().encode())
            # add the miner
            hash_base.update(chain[index].getMinedBy().encode())
            # add the messages in order
            for m in chain[index].getMessages():
                hash_base.update(m.encode())
            # the time (different because this is a number, not a string)
            time = int(chain[index].getTimestamp())
            hash_base.update(time.to_bytes(8, 'big'))
            # add the nonce
            hash_base.update(chain[index].getNonce().encode())
            # get the pretty hexadecimal
            hash = hash_base.hexdigest()
            
            # is it difficult enough? Do I have enough zeros?
            if hash[-1 * DIFFICULTY:] != '0' * DIFFICULTY:
                print("Block {} was not difficult enough: {}\n".format(index, hash))
                return False
            else:
                print("Block {} was difficult enough: {}\n".format(index, hash))
                # time.sleep(0.5)
        return True
    
    def validateChain(self, chain):
        for index in range(len(chain)):
            if index > 0:
                hash_base = hashlib.sha256()
                last_hash = chain[index-1].getHash()
                hash_base.update(last_hash.encode())
                # add the miner
                hash_base.update(chain[index].getMinedBy().encode())
                # add the messages in order
                for m in chain[index].getMessages():
                    hash_base.update(m.encode())
                # the time (different because this is a number, not a string)
                timestamp = int(chain[index].getTimestamp())
                hash_base.update(timestamp.to_bytes(8, 'big'))
                # add the nonce
                hash_base.update(chain[index].getNonce().encode())
                # get the pretty hexadecimal
                hash = hash_base.hexdigest()
                # is it the same as the block's hash?
                current_hash = chain[index].getHash()
                # print(f'hash: {hash}')
                # print(f'current_hash: {current_hash}\n')
                # time.sleep(0.5)
                if hash != current_hash:
                    return False
        return True
    
    def verifyNewBlock(self, reply):
        mined_by = reply.get("minedBy")
        messages = reply.get("messages")
        nonce =  reply.get("nonce")
        
        timestamp = reply.get("timestamp")
        height = reply.get("height")
        last_hash = self.chain[-1].getHash()
        hash_base = hashlib.sha256()
        hash_base.update(last_hash.encode())
        hash_base.update(mined_by.encode())
        for m in messages:
            hash_base.update(m.encode())
        time = int(timestamp)
        hash_base.update(time.to_bytes(8, 'big'))
        hash_base.update(nonce.encode())
        hash = hash_base.hexdigest()
        
        if hash[-1 * DIFFICULTY:] != '0' * DIFFICULTY:
            print("Block {} was not difficult enough: {}\n".format(reply.get("height"), hash))
        else:
            self.chain.append(Block(mined_by, messages, nonce, hash, height, timestamp))
            print(f'Added new block to top of chain!\n')
        
    def sendChainData(self, list):
        last_hash = self.chain[-1].getHash()
        content = {
            "type": "STATS_REPLY",
            "height": len(self.chain),
            "hash": last_hash
        }        
        json_content = json.dumps(content)
        for peer in list:
            host = peer.get("host")
            port = peer.get("port")
            self.peer_socket.sendto(json_content.encode(), (host, port))
        print(f'STATS_REPLY sent to peers {list}\n{content}\n')                  

    def forwardGossip(self, reply, num_peers):
        try:
            peers = []
            json_reply = json.dumps(reply)
            # Forward the gossip message up tp 3 peers
            selected_peers = random.sample(self.peer_list, min(num_peers, len(self.peer_list)))
            selected_host_port = [(peer["host"], peer["port"]) for peer in selected_peers]
            hosts = [peer[0] for peer in selected_host_port]
            ports = [peer[1] for peer in selected_host_port]
            for i in range(len(selected_host_port)):
                self.peer_socket.sendto(json_reply.encode(), (hosts[i], ports[i]))     
                peers.append((hosts[i], ports[i]))    
            print(f'GOSSIP forwarded to {peers}!\n')
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
        except Exception as e:
            print(f'Error forwarding GOSSIP: {e}\n')
    
    def sendGetBlockReply(self, data, address):
        try:
            content = {
                "type": "GET_BLOCK_REPLY",
                **data
            }
            json_content = json.dumps(content)
            self.peer_socket.sendto(json_content.encode(), address)
            print(f'GET_BLOCK_REPLY sent to peer {address}\n')
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
        except Exception as e:
            print(f"Error sending GET_BLOCK_REPLY: {e}")
            sys.exit(1)
        
    def close(self):
        # Close the UDP socket
        self.peer_list = []
        self.stats_data = []
        self.chain = []
        print('\nAll data cleaned!\n')
        self.peer_socket.close()
        print("Socket closed!\n")
        
    def start(self):
        try:
            gossip = self.sendGossipMessage(self.chain_host, self.chain_port)   
            start_time = time.time()
            request_block_time = time.time()
            concensus_time = 0 
            doing_concensus = False
            count = 0
            while True:
                # Resend gossip every 30 seconds
                if time.time() - start_time >= INTERVAL:
                    print(f'BEEN RUNNING FOR {round(time.time() - start_time, 2)} SECONDS\nRE-GOSSIPING!\n')
                    gossip = self.sendGossipMessage(self.chain_host, self.chain_port)
                    self.forwardGossip(gossip, MAX_PEERS) # Forward my GOSSIP up to 3 other known peers
                    start_time = time.time() # track new time

                # Continuously request for blocks if chain is not full
                if time.time() - request_block_time >= WAIT_BLOCK and any(block is None for block in self.chain):
                    print(f'CHAIN IS NOT FULL! REQUESTING FOR MORE BLOCKS...\n')
                    self.doConsensus(self.stats_data)
                    doing_concensus = True
                    request_block_time = time.time()
                
                # Check if the chain is now valid
                if self.chain and all(block is not None for block in self.chain) and doing_concensus and self.validateChain(self.chain):
                    print(f'CHAIN IS NOW VALID! CONTINUE GOSSIPING AND SENDING DATA...\n')
                    # Chain just became valid, set the flag to False and reset the consensus timer
                    concensus_time = time.time()  # Reset consensus time to start the 1-minute wait
                    doing_concensus = False
                    
                # Redo concensus every 1 minute when chain is valid
                if self.chain and all(block is not None for block in self.chain) and time.time() - concensus_time >= INTERVAL and self.validateChain(self.chain):
                    print(f'TIME TO RE-DO CONSENSUS...\n')
                    doing_concensus = True
                    self.doConsensus(self.stats_data)
                
                response, address = self.peer_socket.recvfrom(BUFFER_SIZE)
                data = response.decode()
                if data:
                    try:
                        # convert json to dict
                        reply = json.loads(data)
                        # Extract necessary data
                        request = reply.get("type")
                        if reply.get("host") and reply.get("port"):
                            peer_host = reply.get("host")
                            peer_port = reply.get("port")
                        
                            peer_data = {
                                "host": peer_host,
                                "port": peer_port,
                            }
                            
                        if request == "GOSSIP_REPLY" and peer_host != SILLY_GOOSE and reply.get("name") != USERNAME: # track peer and send STATS 
                            if peer_data not in self.peer_list:
                                print(f'{reply}\n')
                                self.trackPeer(peer_data)
                                if self.peer_list:
                                    print(f'Sending STATS to peers\n')
                                    for peer in self.peer_list:
                                        self.sendStatsMessage(peer["host"], peer["port"])
                                doing_concensus = True
                        # Only reply to GOSSIPs from unknown peers (no self-reply, no reply to peers I just replied to)
                        elif request == "GOSSIP" and reply.get("id") != gossip.get("id") and peer_host != SILLY_GOOSE:
                            # reply to the originate sender
                            if peer_data not in self.peer_list:
                                print(f'{reply}\n')
                                self.trackPeer(peer_data)
                                self.sendGossipReply(address)
                                if self.peer_list:
                                    print(f'Sending STATS to peers\n')
                                    for peer in self.peer_list:
                                        self.sendStatsMessage(peer["host"], peer["port"])
                                # forward that message to at most 3 of my known peers
                                self.forwardGossip(reply, MAX_PEERS) 
                        elif request == "STATS":
                            if self.chain and all(entry is not None for entry in self.chain): # only send if we have data
                                print(f'{reply}\n')
                                self.sendChainData(self.peer_list)
                                doing_concensus = False
                        elif request == "STATS_REPLY" and reply["height"] is not None and int(reply["height"]) > 0 and reply["hash"] is not None:
                            print(f'{reply}\n')
                            self.handleStatsReply(reply, address)
                        elif request == 'GET_BLOCK' and reply.get("height") is not None:
                            height = int(reply.get("height"))
                            if self.chain and all(block is not None for block in self.chain):
                                if height >= 0 and height < len(self.chain) and self.chain[height] is not None:
                                    block_data = self.chain[height].getBlockData()
                                    self.sendGetBlockReply(block_data, address)
                                else:
                                    content = {
                                        "type": "GET_BLOCK_REPLY",
                                        "hash": None,
                                        "height": None,
                                        "messages": None,
                                        "minedBy": None,
                                        "nonce": None,
                                        "timestamp": None
                                    }
                                    self.sendGetBlockReply(content, address)
                        elif request == 'GET_BLOCK_REPLY' and reply.get("height") is not None:
                            height = int(reply.get("height"))
                            if self.chain[height] == None and height >= 0:
                                print(f'{reply}\n')
                                self.handleGetBlockReply(reply, count)
                                count += 1
                                print(f'Received {count}/{len(self.chain)} block(s) from peers!\n')
                        elif request == 'CONCENSUS' and self.chain:
                            if doing_concensus:
                                print(f'{reply}\n')
                                print('Forced doing CONCENSUS!\n')
                                self.doing_concensus = True
                                self.doConsensus(self.stats_data)
                            else:
                                print(f'Doing CONCENSUS...\n')
                        elif request == 'ANNOUNCE' and self.chain and all(entry is not None for entry in self.chain): # New block added to chain
                            height = int(reply.get("height"))
                            if height == len(self.chain) + 1:
                                self.verifyNewBlock(reply)
                        # time.sleep(0.5) # wait for 2 seconds before proceed
                    except json.JSONDecodeError as e:
                        print("Failed to decode JSON in main loop:", e)
        except Exception as e:
            print(f"Error in main loop: {e}") 
        
if __name__ == "__main__":
    try:
        chain_hostname = CHAIN_HOST
        chain_port = CHAIN_PORT
    except ValueError:
        print("Bad port number")
        sys.exit(1)

    peer = Peer(chain_hostname, chain_port) # connect this peer to chain on silicon
    
    try:
        peer.start()
    except KeyboardInterrupt:
        peer.close()