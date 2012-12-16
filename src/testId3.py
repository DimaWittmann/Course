import unittest, id3v2_4 as parser, io

class UTGoodInput(unittest.TestCase):
    
    test_Strings ={'byte': b'\x20',
                   'string': b'\x64\x69\x6d\x61',
                   'syncsafeint':b'\x7a\x1e',
                   'header': b'\x49\x44\x33\x04\x00\x00\x00\x00\x1f\x76',
                   'frame': b'\x54\x41\x4c\x42\x00\x00\x00\x0c\x00\x03\x43\x6f\x6c\x6c\x65\x63\x74\x69\x6f\x6e\x00'}
    
    def test_readChar(self):
        file=io.BytesIO(self.test_Strings['byte'])
        result=parser.readChar(file)
        self.assertEqual(result, ' ')
        
    def test_readByte(self):
        file=io.BytesIO(self.test_Strings['byte'])
        result=parser.readByte(file)
        self.assertEqual(result, 0x20)
        
    def test_readString(self):
        file=io.BytesIO(self.test_Strings['string'])
        result=parser.readString(file, 4)
        self.assertEqual(result, 'dima')
        
    def test_readInteger(self):
        file=io.BytesIO(self.test_Strings['syncsafeint'])
        result=parser.readInteger(file, numOfBytes=2)
        self.assertEqual(result, 0x3D1E)
        
    def test_parseHeader(self):
        answer = {'version': 4, 'flags': {'Extended header': 0, 'Experimental indicator': 0, 'Unsynchronisation': 0, 'Footer present': 0}, 'id': 'ID3', 'size': 4086}
        file=io.BytesIO(self.test_Strings['header'])
        result = parser.parseHeader(file)
        self.assertEqual(result, answer)
        
    def test_parseFrame(self):
        answer = 22
        file=io.BytesIO(self.test_Strings['frame'])
        result = parser.parseFrame(file)
        self.assertEqual(result, answer)   
        
        
if __name__ == '__main__':
    unittest.main()