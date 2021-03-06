# From https://github.com/janglin/crypto-pkcs7-example/blob/master/pkcs7.py

import binascii
import StringIO

## @param text The padded text for which the padding is to be removed.
# @exception ValueError Raised when the input padding is missing or corrupt.
def decode(text, k):
    '''
    Remove the PKCS#7 padding from a text string
    '''
    nl = len(text)
    val = int(binascii.hexlify(text[-1]), 16)
    if val > k:
        raise ValueError('Input is not padded or padding is corrupt')

    l = nl - val
    return text[:l]

## @param text The text to encode.
def encode(text, k):
    '''
    Pad an input string according to PKCS#7
    '''
    l = len(text)
    output = StringIO.StringIO()
    val = k - (l % k)
    for _ in xrange(val):
        output.write('%02x' % val)
    return text + binascii.unhexlify(output.getvalue())
