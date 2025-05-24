import hashlib

DIFFICULTY = 8


b1={   'hash': '9efb33ec9e0ed0a7e837d68d127dff33dba4290ba2535d2312a76f4f00000000',
    'height': 0,
    'messages': [   '3010 rocks',
                    'Warning:',
                    'Procrastinators',
                    'will be sent back',
                    'in time to start',
                    'early.',
                    'Chain 2'],
    'minedBy': 'Prof!',
    'nonce': '967128957948859',
    'timestamp': 1700841637,
    'type': 'GET_BLOCK_REPLY'}

# genesis
# m2 = hashlib.sha256()
# m2.update(b1.get('hash').encode())
# m2.update(b1.get('minedBy').encode())
# for m1 in b1.get('messages'):
#     m2.update(m1.encode())
    
# m2.update(int(b1.get('timestamp')).to_bytes(8, 'big'))
# m2.update(b1.get('nonce').encode())
# print('m2', m2.hexdigest())

# m = hashlib.sha256()
# m.update(b1.get('minedBy').encode())

# # m.update('3010 rocks'.encode()) 
# # m.update('Warning:'.encode()) 
# # m.update('Procrastinators'.encode()) 
# # m.update('will be sent back'.encode()) 
# # m.update('in time to start'.encode()) 
# # m.update('early.'.encode()) 
# # m.update('Chain 2'.encode()) 

# for i in b1.get('messages'):
#     m.update(i.encode())

# m.update(int(b1.get('timestamp')).to_bytes(8, 'big')) # when

# # m.update('967128957948859'.encode()) # nonce
# m.update(b1.get('nonce').encode()) # nonce

# print(m.hexdigest()) # is

# print('9efb33ec9e0ed0a7e837d68d127dff33dba4290ba2535d2312a76f4f00000000\n') # should be


#next block
b2 = {   'hash': 'f736b5ab33d68fd5f9a45e3ecf48615af1db8a2543e3e0d9bb5063bd00000000',
    'height': 1,
    'messages': [   'cattiness',
                    'carousal',
                    'nominees',
                    "Hokkaido's",
                    'overtimes',
                    "freebie's",
                    'beastliest',
                    'Brazil',
                    'jinricksha',
                    'renewed'],
    'minedBy': 'Prof!',
    'nonce': '9459302409010',
    'timestamp': 1700872826,
    'type': 'GET_BLOCK_REPLY'}

m = hashlib.sha256()

# m = hashlib.sha256()
# # m.update('9efb33ec9e0ed0a7e837d68d127dff33dba4290ba2535d2312a76f4f00000000'.encode())
# # print(b1.get('hash'))
# m.update(b1.get('hash').encode())

# m.update('Prof!'.encode())
# m.update('cattiness'.encode())
# m.update('carousal'.encode())
# m.update('nominees'.encode())
# m.update("Hokkaido's".encode())
# m.update('overtimes'.encode())
# m.update("freebie's".encode())
# m.update('beastliest'.encode())
# m.update('Brazil'.encode())
# m.update('jinricksha'.encode())
# m.update('renewed'.encode())
# m.update(int(1700872826).to_bytes(8,'big'))
# m.update('9459302409010'.encode())

# print('f736b5ab33d68fd5f9a45e3ecf48615af1db8a2543e3e0d9bb5063bd00000000')
# print(m.hexdigest())

chain = [b1, b2]

for index in range(len(chain)):
    hash_base = hashlib.sha256()
    if index > 0:
        print(f'last hash: {chain[index-1].get("hash")}')
        hash_base.update(chain[index-1].get("hash").encode())
    
    print(chain[index].get('minedBy'))
    hash_base.update(chain[index].get('minedBy').encode())
    
    for m in chain[index].get('messages'):
        print(m)
        hash_base.update(m.encode())
            
    print(int(chain[index].get('timestamp')))
    hash_base.update(int(chain[index].get('timestamp')).to_bytes(8, 'big'))
    
    print(chain[index].get('nonce'))
    hash_base.update(chain[index].get('nonce').encode())
    
    hash = hash_base.hexdigest()
    
    if hash[-1 * DIFFICULTY:] != '0' * DIFFICULTY:
        print("Block {} was not difficult enough: {}\n".format(index, hash))
    else:
        print("Block {} was difficult enough: {}\n".format(index, hash))