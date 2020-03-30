import nfc

def check_services(tag, start, n):
    services = [nfc.tag.tt3.ServiceCode(i >> 6, i & 0x3f)
                for i in range(start, start+n)]
    versions = tag.request_service(services)
    for i in range(n):
        if versions[i] == 0xffff: continue
        print(services[i], versions[i])

def on_connect(tag):
    print(tag)
    n = 32
    for i in range(0, 0x10000, n):
        check_services(tag, i, n)

def main():
    with nfc.ContactlessFrontend('usb') as clf:
        clf.connect(rdwr={'on-connect': on_connect})

if __name__ == '__main__':
    main()
