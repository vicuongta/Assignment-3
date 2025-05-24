
class Block:
    def __init__(self, mined_by, messages, nonce, hash, height, timestamp):
        self.mined_by = mined_by
        self.messages = messages
        self.nonce = nonce
        self.hash = hash
        self.height = height
        self.timestamp = timestamp
        
    def getMinedBy(self):
        return self.mined_by
        
    def getMessages(self):
        return self.messages
    
    def getNonce(self):
        return self.nonce
    
    def getHash(self):
        return self.hash
    
    def getHeight(self):
        return self.height
    
    def getTimestamp(self):
        return self.timestamp
        
    def getBlockData(self):
        return {
            "hash": self.hash,
            "height": self.height,
            "messages": self.messages,
            "minedBy": self.mined_by,
            "nonce": self.nonce,
            "timestamp": self.timestamp
        }