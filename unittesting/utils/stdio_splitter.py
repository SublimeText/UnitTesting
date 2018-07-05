class StdioSplitter:
    def __init__(self, io, stream):
        self.io = io
        self.stream = stream

    def write(self, data):
        self.io.write(data)
        self.stream.write(data)

    def writeln(self, s):
        self.write(s + "\n")

    def flush(self):
        self.io.flush()
        self.stream.flush()
