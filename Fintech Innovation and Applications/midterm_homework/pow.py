import hashlib
from binascii import unhexlify, hexlify
import time
import datetime


MAX_NONCE = 1000000000000


def sha_256(text):
    return hashlib.sha256(text).digest()

def reverse(str_):
    str_  =  bytearray.fromhex(str_)
    str_.reverse()
    s = ''.join(format(x, '02x') for x in str_)
    return s


def mine(version, prev_block, merkle_root, timestamp, bits):
    start  = time.time()
   
    ##### switch to mode 0 for mining #####
    mode  = 1
    nonce = 0x7c2bac1d 
    prefix_zeros = 0
    for i, s in enumerate(prev_block):
        if s != "0":
            break
        else:
            prefix_zeros += 1
    # print(prefix_zeros)
    prefix_str = '0'* prefix_zeros
    ##### switch to mode 1 for verifying the hash #####

    # nonce = 0x0
    
    # print(f"start mining at : {start}")
    # version
    version = "{0:x}".format(int(version)).zfill(8)
    # print(version)
    version = reverse(version)
    # print(f"version:{version}")
    # prev_block
    prev_block = reverse(prev_block)
    # print(f"prevblock:{prev_block}")
    # merkle_root
    merkle_root = reverse(merkle_root)
    # print(f"merkleroot:{merkle_root}")
    #timestamp
    timestamp = time.mktime(datetime.datetime.strptime(timestamp,"%Y-%m-%d %H:%M:%S").timetuple())
    timestamp = "{0:x}".format(int(timestamp)).zfill(8)
    timestamp = reverse(timestamp)
    # print(f"timestamp:{timestamp}")
    #bits
    bits = "{0:x}".format(int(bits)).zfill(8)
    bits = reverse(bits)
    # print(f"bits:{bits}")


    if(mode==0):
        for nonce in range(MAX_NONCE):
            # nonce = 0
            nonce = "{0:x}".format(int(nonce)).zfill(8)
            nonce = reverse(nonce)
            print(f"Trying nonce:{nonce}")
            # print(f"nonce:{nonce}")
            text = str(version)+str(prev_block)+str(merkle_root)+str(timestamp)+str(bits)+str(nonce)
            
            
            text = unhexlify(text)
            # print(f"text:{text}")
            new_hash = sha_256(sha_256(text))
            new_hash = hexlify(new_hash[::-1]).decode("utf-8")
            # print(f"hash: {new_hash}")
            # count = '0'*8
            if new_hash.startswith(prefix_str):
                print(f"nonce value:{nonce}")
                total_time = str((time.time()-start))
                print(f"total_time:{total_time} seconds")
                print(f"the hash value is: {new_hash}")
                return new_hash
        raise BaseException(f"Couldn't find trying:{MAX_NONCE} times") 
    else :
            
            nonce = "{0:x}".format(int(nonce)).zfill(8)
            nonce = reverse(nonce)
            # print(f"nonce value:{nonce}")
            text = str(version)+str(prev_block)+str(merkle_root)+str(timestamp)+str(bits)+str(nonce)        
            text = unhexlify(text)
            # print(f"text:{text}")
            new_hash = sha_256(sha_256(text))
            new_hash = hexlify(new_hash[::-1]).decode("utf-8")
            new_non = reverse(nonce)
            print(f"the hash value is: {new_hash} with nonce: 0x{new_non}")
