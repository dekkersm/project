__author__ = 'Cyber-01'
import socket
import select
import struct
import sys

# List to keep track of socket descriptors
CONNECTION_LIST = []
RECV_BUFFER = 4096  # Advisable to keep it as an exponent of 2
PORT = 5000
MULTICAST_IP = '224.3.29.71'

snapshot = "snapshot"  # TODO connect to database


def multicast_data(snapshot):
    print "in multicast"
    multicast_group = (MULTICAST_IP, 10000)

    # Create the datagram socket
    multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Set a timeout so the socket does not block indefinitely when trying
    # to receive data.
    multicast_socket.settimeout(10)

    # Set the time-to-live for messages to 1 so they do not go past the
    # local network segment.
    ttl = struct.pack('b', 1)
    multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    try:
        # Send data to the multicast group
        print >>sys.stderr, 'sending "%s"' % snapshot
        sent = multicast_socket.sendto(snapshot, multicast_group)

        # Look for responses from all recipients
        while True:
            print >>sys.stderr, 'waiting to receive'
            try:
                data, server = multicast_socket.recvfrom(16)
            except socket.timeout:
                print >>sys.stderr, 'timed out, no more responses'
                break
            else:
                print >>sys.stderr, 'received "%s" from %s' % (data, server)
                message = raw_input("reply: ")
    finally:
        print >>sys.stderr, 'closing socket'
        multicast_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# this has no effect, why ?
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(("0.0.0.0", PORT))
server_socket.listen(10)
# Add server socket to the list of readable connections
CONNECTION_LIST.append(server_socket)

print "Chat server started on port " + str(PORT)

while True:
    print "in while"
    # Get the list sockets which are ready to be read through select
    read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [], 2)
    for sock in read_sockets:
        print "in read"
        #New connection
        if sock == server_socket:
            # Handle the case in which there is a new connection recieved through server_socket
            sockfd, addr = server_socket.accept()
            CONNECTION_LIST.append(sockfd)
            print >>sys.stderr, "Client (%s, %s) connected" % addr

            new_client_message = (sockfd, "[%s:%s] entered room\n" % addr)  # TODO new client message to c
        #Some incoming message from a client
        else:
            # Data recieved from client, process it
            try:
                #In Windows, sometimes when a TCP program closes abruptly,
                # a "Connection reset by peer" exception will be thrown
                data = sock.recv(RECV_BUFFER)
                if data:
                    snapshot += data  # update snapshot
            except:
                offline_client_message = (sock, "Client (%s, %s) is offline" % addr)  # TODO client offline message to console
                print >>sys.stderr, "Client (%s, %s) is offline" % addr
                sock.close()
                CONNECTION_LIST.remove(sock)
    multicast_data(snapshot)
server_socket.close()