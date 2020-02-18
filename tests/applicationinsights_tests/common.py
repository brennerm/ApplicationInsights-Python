class MockSynchronousSender:
    def __init__(self, send_buffer_size=1):
        self.send_buffer_size = send_buffer_size
        self.data = []
        self.queue = None
        self.start_call_count = 0

    def start(self):
        self.start_call_count += 1

    def send(self, data_to_send):
        self.data.append(data_to_send)