def addr_str(*argv):
    if len(argv) == 1:
        return f'{argv[0][0]}:{argv[0][1]}'
    elif len(argv) == 2:
        return f'{argv[0]}:{argv[1]}'


def addr_tuple(*argv):
    if len(argv) == 1:
        tuple(argv[0].split(':'))
    elif len(argv) == 2:
        return (argv[0][0], argv[1][0])


def addr_tuple(addr):
    return


def get_host(addr):
    if type(addr) is tuple:
        return addr[0]
    else:
        return addr.split(':')[0]


def get_port(addr):
    if type(addr) is tuple:
        return int(addr[1])
    else:
        return int(addr.split(':')[1])
