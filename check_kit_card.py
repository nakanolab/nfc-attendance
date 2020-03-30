import nfc
from binascii import hexlify

SYS_CODE = 0x93B1
SERVICE   = 64
BLOCK = 0

def on_connect(tag):
    idm, pmm = tag.polling(system_code=SYS_CODE)
    tag.idm, tag.pmm, tag.sys = idm, pmm, SYS_CODE

    sc = nfc.tag.tt3.ServiceCode( SERVICE, 0x0b)  
    bc = nfc.tag.tt3.BlockCode( BLOCK, service=0)
    # print(sc)
    # print(bc)

    data = tag.read_without_encryption([sc], [bc])
    print('str:', data)
    print('hex:', hexlify(data))

def main():
    with nfc.ContactlessFrontend('usb') as clf:
        clf.connect(rdwr={'on-connect': on_connect})

if __name__ == '__main__':
    main()
