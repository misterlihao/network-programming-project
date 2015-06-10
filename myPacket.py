import struct

packet_len_pack_pattern = 'Q'
sizeBytes = 8

def sendPacket(sock, bstr):
	sock.send(struct.pack(packet_len_pack_pattern, len(bstr)))
	sock.sendall(bstr)

def recvPacket(sock):
	packet_len_bstr = recvBytes(sock, sizeBytes)
	packet_len = struct.unpack(packet_len_pack_pattern, packet_len_bstr)[0]
	bstr = recvBytes(sock, packet_len)
	print(bstr)
	return bstr

def recvBytes(sock, count):
	bstr = b''
	while count > 0:
		b = sock.recv(count)
		count -= len(b)
		bstr += b
	return bstr
