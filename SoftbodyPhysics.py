import pygame
import random
import math
import time
pygame.init()

screen_width = 800
screen_height = 800
# Set up the display.
screen = pygame.display.set_mode((screen_width, screen_height))

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)


k = 2.8
dampen = 0.2
# k = 2.8
# dampen = 0.15
# k = 3
# dampen = 0.4
# k = 1
# dampen = 0.7
particle_size = 25

class Vec2:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)
    
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)


class Particle:
    position = Vec2()
    velocity = Vec2()
    width = 10
    height = 10
    radius = 10
    color = WHITE
    speed = 10

    def __init__(self, x, y, size, color):
        self.position = Vec2(x, y)
        self.width = size
        self.height = size
        self.radius = size/2
        self.color = color
        self.speed = 10
        self.velocity = Vec2(0, 0)

    def update(self):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

    def rect(self):
        return pygame.Rect(self.position.x-self.radius, self.position.y-self.radius, self.width, self.height)
    
class Spring:
    def __init__(self, pivot, bob):
        self.pivot = pivot
        self.bob = bob
        self.offset = bob.position - pivot.position

    def update(self):
        x = self.bob.position - (self.pivot.position + self.offset)
        self.bob.velocity.x += -k*x.x
        self.bob.velocity.y += -k*x.y
        self.bob.velocity.x *= dampen
        self.bob.velocity.y *= dampen

    def draw(self):
        pygame.draw.line(screen, (RED), (self.pivot.position.x, self.pivot.position.y), (self.bob.position.x, self.bob.position.y))


class Circle(Particle):
    def __init__(self, position):
        self.position = Vec2(position.x, position.y)
        self.particles = [Particle(self.position.x, self.position.y, 10, RED)]
        self.springs = []

        # Create particles
        # for i in range(36):
        #     self.particles.append(Particle(self.position.x + (100*math.cos((math.pi*i*10)/180)), self.position.y + (100*math.sin((math.pi*10*i)/180)), particle_size, WHITE))
        for i in range(10):
            self.particles.append(Particle(self.position.x + (100*math.cos((math.pi*i*36)/180)), self.position.y + (100*math.sin((math.pi*36*i)/180)), particle_size, WHITE))
            
        # Create springs
        for i in range(0, len(self.particles)-1):
            self.springs.append(Spring(self.particles[i], self.particles[i+1]))
         # close loop
        # self.springs.append(Spring(self.particles[len(self.particles)-1], self.particles[0]))
        self.springs.append(Spring(self.particles[1], self.particles[len(self.particles)-1]))

        for i in range(1, len(self.particles)):
            self.springs.append(Spring(self.particles[i], self.particles[0]))

shapes = [
    Circle(Vec2(screen_width/2, screen_height/2)),
    Circle(Vec2(0, 0))
]
grabbing = None
def update():
    global grabbing
    (x, y) = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:
        if grabbing == None:
            for shape in shapes:
                if shape.rect().collidepoint(x, y):
                    grabbing = shape
                for particle in shape.particles:
                    if particle.rect().collidepoint(x, y):
                        grabbing = particle
        else:
            grabbing.position.x = x
            grabbing.position.y = y
            grabbing.velocity.x = 0
            grabbing.velocity.y = 0

    if pygame.mouse.get_just_released()[0]:
        grabbing = None

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        shapes[0].particles[0].velocity.x -= 10
    if keys[pygame.K_d]:
        shapes[0].particles[0].velocity.x += 10
    if keys[pygame.K_w]:
        shapes[0].particles[0].velocity.y -= 10  
    if keys[pygame.K_s]:
        shapes[0].particles[0].velocity.y += 10

    
    for shape in shapes:
        shape.update()
        for particle in shape.particles:
            particle.update()
        for spring in shape.springs:
            spring.update()
        

            
def draw():
    # Fill the screen with white
    screen.fill((0,0,0))
    
    for shape in shapes:
        for particle in shape.particles:
            r = max(50, min(abs(particle.velocity.x), 255))
            g = max(50, min(abs(particle.velocity.y), 255))
            pygame.draw.circle(screen, (r, g, 0), (particle.position.x, particle.position.y), particle.radius)
        for spring in shape.springs:
            spring.draw()
        


    # Update the display
    pygame.display.flip()

frames = 0
fps = 0
# The game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    update()
    draw()
    # Control the frame rate
    pygame.time.Clock().tick(60)

pygame.quit()