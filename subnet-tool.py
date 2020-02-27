from optparse import OptionParser
import sys

addzero= lambda x : ( x not in "10" ) and '0' or x

def ip2network_address(ip='192.168.1.0', cidr='32'):
    """
    This func also corrects wrong subnet, e.g.
    if found 10.69.231.70/29, it'll be corrected to 10.69.231.64/29.
    """
    ip = ip.split('.')
    netmask = cidr2mask(cidr)
    bin_mask_list = ip2binlist(netmask)
    for x in range(len(ip)):
        ip[x] = int(ip[x]) & int(bin_mask_list[x], 2)
    if int(cidr) < 31:
        network_address = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
        first_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3]+1)
        avail_host_numbers = 2 ** (32 - int(cidr)) - 2
        complement_bin_list = mask2complement_bin_list(netmask)
        broadcast_address = '.'.join([ str(ip[x]+int(complement_bin_list[x],2)) for x in range(4)])
        last_avail_ip_list = broadcast_address.split('.')[0:3]
        last_avail_ip_list.append( str( int(broadcast_address.split('.')[-1]) -1 ) )
        last_avail_ip = '.'.join(last_avail_ip_list)
    elif int(cidr) == 31:
        broadcast_address = network_address = None
        first_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
        last_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3]+1)
        avail_host_numbers = 2
    else:
        broadcast_address = network_address = None
        first_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
        last_avail_ip = first_avail_ip
        avail_host_numbers = 1
    return  avail_host_numbers, netmask, network_address, first_avail_ip,last_avail_ip, broadcast_address

def cidr2mask(cidr='24'):
    cidr=int(cidr)
    fullnet = '0b11111111'
    zeronet = '0b00000000'
    if cidr <= 8:
        hosts = 8 - cidr
        net = '0b' + '1'* cidr + '0' * hosts
        net = (net, zeronet, zeronet, zeronet)
    elif 8 < cidr <= 16:
        hosts = 16 - cidr
        net = '0b' + '1'* (cidr-8) + '0' * hosts
        net = (fullnet, net, zeronet, zeronet)
    elif 16 < cidr <= 24:
        cidr = cidr - 16
        hosts = 8 - cidr
        net = '0b' + '1'* cidr + '0' * hosts
        net = (fullnet, fullnet, net, zeronet)
    else:
        cidr = cidr - 24
        hosts = 8 - cidr
        # print cidr,hosts
        net = '0b' + '1'* cidr + '0' * hosts
        net = (fullnet, fullnet, fullnet, net)
    netmask = '.'.join([ str(int(net[x], 2)) for x in range(len(net)) ])
    return netmask

def cidr2hex(cidr='24'):
    netmask = cidr2mask(cidr)
    bin_mask_list = ip2binlist(netmask)
    hex_list = [ hex(int(b,2)).split('0x')[1].upper() for b in bin_mask_list ]
    return hex_list

    
def mask2cidr(mask='255.255.255.0'):
    '''
    1.  '255.11111.266.4' to '255.255.255.0' to 24
    2.  '255.128.255.0'  to 9
    '''
    mask_list = mask.split('.')
    mask_list = map(int,mask_list)                          # int list
    notexcess = lambda x: ( x > 255) and 255 or x          # if any one bigger than 255, set to 255
    # addzero= lambda x : ( x not in "10" ) and '0' or x    # set as global func
    mask_list = map(notexcess, mask_list)
    binmask_total=''
    for x in mask_list:
    #for x in range(4):
        binmask = "%8s" %bin(x).split('0b')[1]   #  '    1101'
        binmask = ''.join(map(addzero,list(binmask)))       #  '00001101'  , addzero
        binmask_total += binmask
    try:
        zindex = binmask_total.index('0')
    except ValueError:
        zindex = 32
    return  zindex


def main():

    parser = OptionParser(add_help_option=False)
    parser.add_option('-i', '--ip',
                                dest='ip', )
    parser.add_option('-c', '--cidr',
                                dest='cidr',
                                help='Specify the cidr of mask to query. e.g. --cidr 24, indicates mask=255.255.255.0')
    parser.add_option('-m', '--mask',
                                dest='mask',
                                help='Specify the Dotted Decimal mask to query. e.g. -m 255.255.0.0')
    parser.add_option('-h', '--host_amount',
                                dest='host_amount',
                                help='Specify the number of available hosts we want in each subnet.')
    parser.add_option('-s', '--subnet_amount',
                                dest='subnet_amount',
                                help='Specify the number of subnets we want.')
    parser.add_option('-M', '--mode',
                                dest='mode',
                                help='Specify  Mode 1-9 to calculate or transfer.')
    def option_without_param(option, opt_str, value, parser):
        parser.values.details = True

    parser.add_option("-a","--all", action="callback", callback=option_without_param, help='Details will be shown')
    parser.add_option('-?', '--help',
                                action='store_true',
                                help='--help --all shows Mode details.')
    (options, args) = parser.parse_args()



    ip  =   options.ip
    cidr = options.cidr
    mask = options.mask
    host_amount = options.host_amount
    subnet_amount = options.subnet_amount
    mode = options.mode

    try:
        if  options.details:
            details = options.details
    except AttributeError:
        details = None

    if options.help :
        parser.print_help()
        if details or mode:
            help_info(mode)
        parser.exit()

    if (ip or cidr or mask or host_amount or subnet_amount) is None:
        parser.print_help()
        if details or mode:
            help_info(mode)
        parser.exit()

    try:
        '''
        parameter auto-adjustment
        '''
        if cidr and (mask is None):
            mask = cidr2mask(cidr)
        if mask and (cidr is None):
            cidr = mask2cidr(mask)
        '''
        Different Modes
        '''
        if mode == '1' :
            result = ip2network_address(ip,cidr)
        elif mode == '2':
            mask = cidr2mask(cidr)
            hex = cidr2hex(cidr)
            result = (mask, '.'.join(hex))



if __name__ == '__main__':
    main()