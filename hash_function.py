# By Sawyer, Griffin, and Rahil
# Custom hashing function for Olin College Discrete Math 2015

import sys
import math
import bitstring
from bitstring import BitArray, BitStream, ConstBitStream
from Crypto.Hash import MD5
from random import randint
import numpy
import matplotlib.pyplot as plt

def padBits(input, bitSize):
    """
    This function will pad our input to a multiple of the block size
    it will pad 
    """
    # if 0 bits, just return a block with 1000000000
    if len(input.bin) == 0:
        command = 'bin:1=1, bin:' + str(bitSize-1) + '=' + '0'*(bitSize-1)
        return bitstring.pack(command)
    #if length of the input is a multiple of block size, 
    length = len(input.bin)
    remainder = length % bitSize
    remainder = bitSize - remainder
    if remainder == 0:
        remainder = bitSize
    zeroBits = remainder - 1
    zeros = '0'*zeroBits
    command = 'bin:'+str(length)+'='+input.bin+', bin:1=1, bin:' + str(zeroBits) + '=' + zeros
    return bitstring.pack(command)
    
def leftShift(x,n):
    """ 
    This function performs logical left shift
    """
    for i in range(n):
        bits = x.bin
        finalBit = bits[0]
        leftShiftedBits = (x<<1).bin
        leftShiftedBits = leftShiftedBits[:-1] + finalBit
        x = BitArray('0b'+leftShiftedBits)
    return x
    
def rightShift(x,n):
    """ 
    This function performs logical right shift
    """
    for i in range(n):
        bits = x.bin
        finalBit = bits[len(bits)-1]
        rightShiftedBits = (x>>1).bin
        rightShiftedBits = finalBit + rightShiftedBits[1:]
        x = BitArray('0b'+rightShiftedBits)
    return x
    
def add(x,y,bits):
    '''
    We had to write a function to add two BitArrays because the '+' operator just concats them
    '''
    a = (x.uint + y.uint) % (2**bits)
    return BitArray("uint:"+str(bits)+"="+str(a))
    
def truncate(x,n):
    ''' 
    This function takes a BitArray and truncates it to n bits
    '''
    bits = x.bin
    newBits = bits[-n:]
    return BitArray('0b'+newBits)
    
def j(x,y,z):
    """
    This function does stuff inside of our compression
    it should be (x v y) XOR (~z ^ y)
    """
    a = (x | y) ^ (~z & y)
    return a
    
def k(x,y,z):
    """
    This function does stuff inside our compressionFunction
    it should be (~x XOR y) v (z ^ ~x)
    """
    a = (~x ^ y) | (z ^ ~x)
    return a

def compressionFunction(input1, input2, bitSize):
    """
    This function runs our compression function. The portion of code inside the
    main for loop is our round function e(), which is run on input2, which is the
    current block. The round function is looped through by the number of rounds 
    specified in the function (64 in this case). The round function utilizes addition, 
    shifts, and two functions j() and k(). At the end, the output of the round 
    function() is XORed with input1, which is the hashed version of the previous 
    block. The output of the XOR operation is returned by the function.
    
    The bitSize input is necessary to split each block into four sub-blocks of the
    correct size.
    """
    alpha = 'abcd'
    subBitSize = bitSize / 4
    rounds = 64
    
    for x in range(rounds):
        blocks = {}
        newBlocks = {}
        
        for y in range(4):
            blocks[alpha[y]] = input2[y*subBitSize:y*subBitSize+subBitSize]
        
        shiftSize = subBitSize / 2 - 1
        a_j = j(blocks['a'], blocks['b'], blocks['c'])
        a_k = k(blocks['a'], a_j, blocks['d'])
        newBlocks['a'] = add(a_k, blocks['b'], subBitSize)
        newBlocks['b'] = blocks['a']
        newBlocks['c'] = leftShift(blocks['d'], shiftSize)
        newBlocks['d'] = add(blocks['b'], blocks['c'], subBitSize)
        
        for z in range(4):
            input2[z*subBitSize:z*subBitSize+subBitSize] = newBlocks[alpha[z]]

    output = input1 ^ input2
    
    return output
    
def merkle(messageBlock, bitSize, initialValue, padFunction, compressionFunction):
    """
    The merkle calls our compression function multiple times
    once for each  message block 
    """
    
    # pad the bits
    messageBlock = padFunction(messageBlock, bitSize)
    
    #setup
    prevState = initialValue
    
    # loop through messages
    numMessages = len(messageBlock.bin)/bitSize
    for i in range(numMessages):
        shortMessage = messageBlock[bitSize*i:bitSize*(i+1)] # get current message
        prevState = compressionFunction(prevState, shortMessage, bitSize) # call compressionFunction
    
    return prevState
    
def runMerkle(hashInput):
    """
    This just runs the merkle given a certain input. It uses all of the global variables
    defined in main to run the merkle function
    """
    return merkle(hashInput, bitSize, iv, padBits, compressionFunction)
    
def percentSimilar(a,b):
    '''
    Returns the percentage of bits that are the same in a and b
    '''
    if len(a) != len(b):
        print("Input same size numbers")
        return
    
    count = 0
    for i in range(len(a)):
        if (a[i] == b[i]):
            count+=1
            
    return float(count) / len(a)

def avalanche_test_compression(iters, bitSize):
    """
    This function will test whether a given compression function produces good 
    avalanche effect. To do this we'll change one bit at random, roughly 50% 
    of the output bits should flip. In order to test this, we'll generate
    a bunch of random bitstrings, pick random bit to flip for each one,
    run the compression function, and do this many times in a row for each 
    bitstring. At the end we'll monitor the average % of bits that flipped, 
    as well as the minimum % and maximum % flipped
    
    Inputs: iters = number of iterations to run
    bitSize = the size of the input, please make this a power of 2
    """
    similarPercents = []
    prevState = BitArray('0b'+make_random_bitstring(bitSize))
    #short array will be the same every time
    shortMessage = BitArray('0b'+make_random_bitstring(bitSize))
   
    #however many iterations of compression we want to do
    for i in range(0,iters):
        #now run compression on it
        new_message = compressionFunction(prevState, shortMessage, bitSize)
        #check how similar they are
        percentSim = percentSimilar(new_message, prevState)
        #add the percent similar to our list
        similarPercents.append(percentSim)
        #make the prev state the new message
        prevState = new_message
    #print similarPercents
    print "compression avalanche percent for " + str(iters) + " tests is: "+str(numpy.mean(similarPercents))
    return
    
def avalanche_test_merkle(iters):
    """
    Run avalanche testing with our full merkle function, not just compression
    """
    print "running merkle avalanche test"
    similarPercents = []
    for i in range(0,iters-1):
        first_bitstring = BitArray('0b'+make_random_bitstring(bitSize))
        flipped_first = flip_random_bit(first_bitstring)
        interim_percent = percentSimilar(runMerkle(first_bitstring), runMerkle(flipped_first))
        similarPercents.append(interim_percent)
    print "merkle avalanche overall percent similar for " + str(iters) + " tests (custom merkle) is: " + str(numpy.mean(similarPercents))
    print "merkle standard deviation for avalanche values (custom merkle) is: " + str(numpy.std(similarPercents))
    #make a histogram of the data
    plt.hist(similarPercents)
    plt.title("Histogram of custom hash avalanche values")
    plt.xlabel("Percent Similar")
    plt.ylabel("Frequency")
    plt.show()
    print "merkle avalanche testing done"

def md5_bitstring_run(input_bitstring):
    md5test = MD5.new()
    md5test.update(make_random_bitstring(bitSize))
    md5_hex = md5test.hexdigest()
    md5_bitstring = BitArray('0x'+md5_hex)
    return md5_bitstring

def avalanche_test_md5(iters):
    """
    run the same avalanche test, but with md4 algorithm so that we can compare
    to our custom algorithm
    """
    
    print "running md5 avalanche test"
    similarPercents = []
    for i in range(0,iters-1):
        first_bitstring = BitArray('0b'+make_random_bitstring(bitSize))
        flipped_first = flip_random_bit(first_bitstring)
        interim_percent = percentSimilar(md5_bitstring_run(first_bitstring), md5_bitstring_run(flipped_first))
        similarPercents.append(interim_percent)
    print "merkle avalanche overall percent similar for " + str(iters) + " tests (md5)  is: " + str(numpy.mean(similarPercents))
    print "merkle standard deviation for avalanche values (md5) is: " + str(numpy.std(similarPercents))
    #make a histogram of the data
    plt.hist(similarPercents)
    plt.title("Histogram of custom hash avalanche values (md5)")
    plt.xlabel("Percent Similar")
    plt.ylabel("Frequency")
    plt.show()
    print "merkle avalanche testing done"

    
def flip_random_bit(first_bitstring):
    """
    Selects a random bit from a bitstring and flips its value
    """
    bits = first_bitstring.bin
    flip_bit_index = randint(0,len(bits)-1)
    new_bitstring = bits[0:flip_bit_index]
    
    if first_bitstring[flip_bit_index]==0:
        new_bitstring += '1'
    else:
        new_bitstring += '0'
        
    new_bitstring += bits[flip_bit_index+1:]
    return BitArray('0b'+new_bitstring)

def make_random_bitstring(length):
    """
    Returns a string of bits of length next
    you'll need to convert to a BitArray
    """
    output_bitstring = "0"
    for i in range(0,length-1):
        #make a randint every time
        output_bitstring += `randint(0,1)`
    return output_bitstring

def collisionTest(digits):
    ''' 
    This function iterates through all possible values up to the number of digits 
    It saves these 
    '''
    collisionDict = {}
    numCollisions = 0
    for i in range(digits):
        numDigits = i+1
        for j in range(2**numDigits):
            hashInput = BitArray('uint:'+str(numDigits)+'='+str(j))
            out = runMerkle(hashInput)
            bin = out.bin
            if out.bin in collisionDict:
                collisionDict[out.bin][0] += 1
                collisionDict[out.bin][1].append(hashInput.bin)
                print("COLLISION")
                numCollisions += 1
                for i in range(len(collisionDict[out.bin][1])):
                    print(collisionDict[out.bin][1][i])
                else:
                    collisionDict[out.bin] = [1, [hashInput.bin]]
    print("Number collisions: "+str(numCollisions))

if __name__=="__main__":
    bitSize = 32
    iv = BitArray('0x0d84fee0')
    
    avalanche_test_compression(100, bitSize)
    avalanche_test_merkle(100)
    avalanche_test_md5(100)
    
    hashInput = BitArray('0x446973637265746520697320617765736f6d6521')
