
class YerFaceFIFOReader:
    def __init__(self):
        self.packets = []

    def insertNextPacket(self, packetObj):
        self.packets.append(packetObj)

    def returnNextPackets(self):
        copyPackets = list(self.packets)
        self.packets = []
        return copyPackets
