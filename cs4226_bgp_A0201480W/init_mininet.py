#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import os

N = 6
DIRPREFIX='/home/sdn/bgp_cases/cs4226_bgp_A0201480W' 
#NOTE: if using relative path, there would be error when creating .pid and .api files

def prefix(address, length):
    return "%s/%s" % (address, str(length))

def start_ripd(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    config = dir + 'ripd.conf'
    zsock  = dir + 'zserv.api'
    pid    = dir + 'ripd.pid'
    r.cmd('/usr/lib/quagga/ripd --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))

def stop_ripd(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    pidfile =  dir + 'ripd.pid'
    f = open(pidfile)
    pid = int(f.readline())
    r.cmd('kill {}'.format(pid))
    info('stoped {} ripd'.format(name))

def start_zebra(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    config = dir + 'zebra.conf'
    pid =  dir + 'zebra.pid'
    log =  dir + 'zebra.log'
    zsock=  dir + 'zserv.api'
    # r.cmd('> {}'.format(log))			# this creates the file with the wrong permissions
    r.cmd('rm -f {}'.format(pid))    	# we need to delete the pid file
    r.cmd('/usr/lib/quagga/zebra --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))


def stop_zebra(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    pidfile =  dir + 'zebra.pid'
    f = open(pidfile)
    pid = int(f.readline())
    zsock=  dir + 'zserv.api'
    r.cmd('kill {}'.format(pid))
    r.cmd('rm {}'.format(zsock))
    info('stoped {} zebra'.format(name))

def start_bgpd(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    config = dir + 'bgpd.conf'
    zsock  = dir + 'zserv.api'
    pid    = dir + 'bgpd.pid'
    r.cmd('/usr/lib/quagga/bgpd --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))

def stop_bgpd(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    pidfile =  dir + 'bgpd.pid'
    f = open(pidfile)
    pid = int(f.readline())
    r.cmd('kill {}'.format(pid))
    info('stoped {} bgpd'.format(name))

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):
    
        r1_eth1 = '10.0.1.1'
        r1_eth2 = '1.1.1.1'
        r1_eth3 = '5.5.5.2'

        r2_eth1 = '10.0.2.1'
        r2_eth2 = '2.2.2.1'
        r2_eth3 = '6.6.6.2'

        r3_eth1 = '3.1.1.1'
        r3_eth2 = '1.1.1.2'
        r3_eth3 = '2.2.2.2'
        r3_eth4 = '3.4.4.1'

        r4_eth1 = '10.0.1.2'
        r4_eth2 = '10.0.2.2'

        r5_eth1 = '5.5.5.1'
        r5_eth2 = '5.1.1.1'

        r6_eth1 = '6.6.6.1'
        r6_eth2 = '6.3.3.1'

        h1_eth0 = '3.1.1.2'
        h2_eth0 = '5.1.1.2'
        h3_eth0 = '6.3.3.2'
        h4_eth0 = '3.4.4.2'

        r1 = self.addNode('r1', cls=LinuxRouter, ip=prefix(r1_eth1, 24))
        r2 = self.addNode('r2', cls=LinuxRouter, ip=prefix(r2_eth1, 24))
        r3 = self.addNode('r3', cls=LinuxRouter, ip=prefix(r3_eth1, 24))
        r4 = self.addNode('r4', cls=LinuxRouter, ip=prefix(r4_eth1, 24))
        r5 = self.addNode('r5', cls=LinuxRouter, ip=prefix(r5_eth1, 24))
        r6 = self.addNode('r6', cls=LinuxRouter, ip=prefix(r6_eth1, 24))

        #the firt inferface to use would be the default ip
        h1 = self.addHost('h1', ip=prefix(h1_eth0, 24), defaultRoute='via {}'.format(r3_eth1))
        h2 = self.addHost('h2', ip=prefix(h2_eth0, 24), defaultRoute='via {}'.format(r5_eth2))
        h3 = self.addHost('h3', ip=prefix(h3_eth0, 24), defaultRoute='via {}'.format(r6_eth2))
        h4 = self.addHost('h4', ip=prefix(h4_eth0, 24), defaultRoute='via {}'.format(r3_eth4))

        self.addLink(h1,r3,intfName2='r3-eth1',params2={ 'ip' : prefix(r3_eth1, 24) })
        self.addLink(h4,r3,intfName2='r3-eth4',params2={ 'ip' : prefix(r3_eth4, 24) })

        self.addLink(r1, r4,
                     intfName1='r1-eth1', params1={'ip': prefix(r1_eth1, 24)},
                     intfName2='r4-eth1', params2={'ip': prefix(r4_eth1, 24)})

        self.addLink(r5, r1,
                     intfName1='r5-eth1', params1={'ip': prefix(r5_eth1, 24)},
                     intfName2='r1-eth3', params2={'ip': prefix(r1_eth3, 24)})
             
        self.addLink(r4, r2,
                     intfName1='r4-eth2', params1={'ip': prefix(r4_eth2, 24)},
                     intfName2='r2-eth1', params2={'ip': prefix(r2_eth1, 24)})
        
        self.addLink(r2, r6,
                     intfName1='r2-eth3', params1={'ip': prefix(r2_eth3, 24)},
                     intfName2='r6_eth1', params2={'ip': prefix(r6_eth1, 24)})
	
        self.addLink(r1, r3,
                     intfName1='r1-eth2', params1={'ip': prefix(r1_eth2, 24)},
                     intfName2='r3-eth2', params2={'ip': prefix(r3_eth2, 24)})

        self.addLink(r3, r2,
                     intfName1='r3-eth3', params1={'ip': prefix(r3_eth3, 24)},
                     intfName2='r2-eth2', params2={'ip': prefix(r2_eth2, 24)})

        self.addLink(h2,r5,intfName2='r5-eth2',params2={ 'ip' : prefix(r5_eth2, 24) })
        self.addLink(h3,r6,intfName2='r6-eth2',params2={ 'ip' : prefix(r6_eth2, 24) })
	


def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet(controller = None, topo=topo )  # controller is used by s1-s3
    net.start()
    info( '*** Routing Table on Router:\n' )
#    info( net[ 'r1' ].cmd( 'route' ) )

    BGPnodelist = []		
    for i in range(1, N+1):
        nodename = 'r{}'.format(i)
        node = net[nodename]
        BGPnodelist.append(node)
    print('BGPnodelist:', BGPnodelist)


    '''
    # now we build zebra.conf
    zconflist = []
    # Create "zebra.conf" file for each router 
    for r in BGPnodelist:
        zconf = create_zebra_conf(r, ndict) 
        zconflist.append(zconf)
    '''
    '''
    bgpconflist = []    
    # Create "bgpd.conf" file for each router
    for r in BGPnodelist:
        bgpconf = create_bgpd_conf(r, ndict, addrdict, ASdict) 
        bgpconflist.append(bgpconf)
    '''

    info('starting zebra and bgpd service:\n')
    idx1 = 0
    for r in BGPnodelist:
        idx1 = idx1 + 1
        start_zebra(r)
        if (idx1 != 4):
            start_bgpd(r)


    r1Node = net['r1']
    r2Node = net['r2']
    r4Node = net['r4']
    
    info('starting r4 zebra, ripd service:\n')
    start_zebra(r4Node)
    start_ripd(r4Node)
    
    info('starting r1 ripd service:\n')
    start_ripd(r1Node)

    info('starting r2 ripd service:\n')
    start_ripd(r2Node)


    
    # print routing table
    for node, type in net.items():
        if isinstance(type, Node):
            info('*** Routing Table on Router %s:\n' % node)
            info(net[node].cmd('route'))    


    CLI( net )
    #os.system("killall -9 bgpd zebra")
    # stop and erase .api .pid files
    
    info('stoping r4 zebra, ripd service:\n')
    stop_ripd(r4Node)
    stop_zebra(r4Node)

    
    info('starting r1 ripd service:\n')
    stop_ripd(r1Node)

    info('starting r2 ripd service:\n')
    stop_ripd(r2Node)
    
    idx = 0
    for r in BGPnodelist:
        idx = idx + 1
        if (idx != 4):
            stop_bgpd(r)
            stop_zebra(r)


    net.stop()
    '''
    for zconf in zconflist:
        print('removing file {}'.format(zconf))
        os.remove(zconf)
    '''
    '''
    for bgpconf in bgpconflist:
        print('removing file {}'.format(bgpconf))
        os.remove(bgpconf)
    '''
    os.system('stty erase {}'.format(chr(8)))

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()

