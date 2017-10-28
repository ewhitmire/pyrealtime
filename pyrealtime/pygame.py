import threading


from pyrealtime.layer import ProcessLayer, TransformMixin


class PyGameLayer(TransformMixin, ProcessLayer):
    def __init__(self, port_in, win_width=640, win_height=480, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.height = win_height
        self.width = win_width
        self.lock = None
        self.clock = None
        self.screen = None
        self.data = None

    def initialize(self):
        try:
            import pygame
        except ImportError:
            print("PyGame required to use this feature")
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.lock = threading.Lock()
        self.clock = pygame.time.Clock()

    def transform(self, data):

        self.lock.acquire()
        self.data = data
        self.lock.release()

    def draw(self):
        raise NotImplementedError

    def get_data(self):
        self.lock.acquire()
        data = self.data
        self.lock.release()
        return data

    def main_thread_post_init(self):
        try:
            import pygame
        except ImportError:
            print("PyGame required to use this feature")
        """ Main Loop """
        while not self.stop_event.is_set():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
            self.clock.tick(50)
            self.draw()

