#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
import os

N=4
DIRPREFIX='/home/mininet/git_workspace/bgp_cases/06_metric_attribute' 
#TODO: Change the absolute
#NOTE: if using relative path, there would be error when creating .pid and .api files

def prefix(address, length):
    return "%s/%s" % (address, str(length))


def start_zebra(r):
    name = '{}'.format(r)
    dir='{}/{}/'.format(DIRPREFIX, name)
    config = dir + 'zebra.conf'
    pid =  dir + 'zebra.pid'
    log =  dir + 'zebra.log'
    zsock=  dir + 'zserv.api'
    # r.cmd('> {}'.format(log))			# this creates the file with the wrong permissions
    r.cmd('rm -f {}'.format(pid))    	# we need to delete the pid file
    r.cmd('/usr/sbin/zebra --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))


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
    r.cmd('/usr/sbin/bgpd --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))

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

        r1_eth0 = '10.0.0.1'
        r1_eth1 = '170.10.0.1'
        h1_eth1 = '170.10.0.2'
        #r1_eth2 = '2.2.2.2'
        r1_eth2 = '13.13.13.1'
        #r1_eth3 = '3.3.3.2'
        r1_eth3 = '14.14.14.1'
        #r1_eth4 = '4.4.4.4'
        r1_eth4 = '12.12.12.1'


        #r2_eth1 = '4.4.4.3'
        r2_eth1 = '12.12.12.2'
        #r2_eth2 = '5.5.5.5'
        r2_eth2 = '24.24.24.1'

        r3_eth1 = '180.10.0.1'
        #r3_eth2 = '2.2.2.1'
        r3_eth2 = '13.13.13.2'
        #r3_eth3 = '1.1.1.1'
        r3_eth3 = '34.34.34.1'


        #r4_eth1 = '1.1.1.2'
        r4_eth1 = '34.34.34.2'
        #r4_eth2 = '3.3.3.3'
        r4_eth2 = '14.14.14.2'
        #r4_eth3 = '5.5.5.4'
        r4_eth3 = '24.24.24.2'

        r4_eth4 = '180.10.0.4'

        s1_eth1 = '180.10.0.2'
        s1_eth2 = '180.10.0.3'


        r1 = self.addNode( 'r1', cls=LinuxRouter, ip=prefix(r1_eth1, 24))
        r2 = self.addNode( 'r2', cls=LinuxRouter, ip=prefix(r2_eth1, 24))
        r3 = self.addNode( 'r3', cls=LinuxRouter, ip=prefix(r3_eth1, 24))
        r4 = self.addNode( 'r4', cls=LinuxRouter, ip=prefix(r4_eth4, 24))
	        
        h1 = self.addHost( 'h1', ip=prefix(h1_eth1, 24), defaultRoute='via {}'.format(r1_eth1)) #define gateway
        s1 = self.addSwitch('s1', ip=prefix(s1_eth1,24))

        self.addLink(h1,r1,intfName2='r1-eth1',params2={ 'ip' : prefix(r1_eth1, 24) })        
        
        self.addLink(r3, s1,
                     intfName1='r3-eth1', params1={'ip': prefix(r3_eth1, 24)},
                     intfName2='s1-eth1', params2={'ip': prefix(s1_eth1, 24)})

        self.addLink(r4, s1,
                     intfName1='r4-eth4', params1={'ip': prefix(r4_eth4, 24)},
                     intfName2='s1-eth2', params2={'ip': prefix(s1_eth2, 24)})


        self.addLink(r1, r2,
                     intfName1='r1-eth4', params1={'ip': prefix(r1_eth4, 24)},
                     intfName2='r2-eth1', params2={'ip': prefix(r2_eth1, 24)})

        self.addLink(r3, r4,
                     intfName1='r3-eth3', params1={'ip': prefix(r3_eth3, 24)},
                     intfName2='r4-eth1', params2={'ip': prefix(r4_eth1, 24)})

        self.addLink(r1, r3,
                     intfName1='r1-eth2', params1={'ip': prefix(r1_eth2, 24)},
                     intfName2='r3-eth2', params2={'ip': prefix(r3_eth2, 24)})
        self.addLink(r1, r4,
                     intfName1='r1-eth3', params1={'ip': prefix(r1_eth3, 24)},
                     intfName2='r4-eth2', params2={'ip': prefix(r4_eth2, 24)})


        self.addLink(r2, r4,
                     intfName1='r2-eth2', params1={'ip': prefix(r2_eth2, 24)},
                     intfName2='r4-eth3', params2={'ip': prefix(r4_eth3, 24)})       


      

	

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
    for r in BGPnodelist:
        start_zebra(r)
        start_bgpd(r)
    
    
    # print routing table
    for node, type in net.items():
        if isinstance(type, Node):
            info('*** Routing Table on Router %s:\n' % node)
            info(net[node].cmd('route'))    


    CLI( net )
    #os.system("killall -9 bgpd zebra")
    # stop and erase .api .pid files
    
    

    for r in BGPnodelist:
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




