import sharppy.io.decoder as decoder

"""
    Unit tests to test to see if decoders work on different file types
"""

def test_decoder():
    files = ['../../examples/data/14061619.OAX',
             '../../examples/data/rap_oun.buf']

 #            '../../examples/data/ABR.txt',
#print(test_decoder('../../examples/data/OUN.txt'))

#import sharppy.io.pecan_decoder as p
#p.PECANDecoder('../../examples/data/ABR.txt')
#   
    decoders = decoder.getDecoders()
    for filename in files:
        for key in decoders.keys():
            print(key)
            try:
                dec = decoders[key](filename)
                 # Returns the set of profiles from the file that are from the "Profile" class.
                profs = dec.getProfiles()
                stn_id = dec.getStnId()
                return profs, stn_id
            except Exception as e:
                print(e)
                continue
