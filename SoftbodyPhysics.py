import pygame
import random
import math
import time
pygame.init()

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
    
screen_width = 800
screen_height = 800
# Set up the display.
screen = pygame.display.set_mode((screen_width, screen_height))
center_x = screen_width / 2
center_y = screen_height / 2
origin = Vec2(center_x, center_y)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

def clamp(value, min, max):
    if value < min:
        value = min
    elif value > max:
        value = max
    return value

k = 1/10
dampen = 0.99
particle_size = 7
class Particle:
    position = Vec2()
    velocity = Vec2()
    width = 10
    height = 10
    radius = 10
    color = WHITE
    speed = 10

    def __init__(self, x, y, size = particle_size, color = WHITE):
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

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.position.x, self.position.y), self.radius)
        
    def rect(self):
        return pygame.Rect(self.position.x-self.radius, self.position.y-self.radius, self.width, self.height)
    
class Spring:
    def __init__(self, pivot, bob, spring_constant_k = 0.01, elastic_limit = 10):
        self.pivot = pivot
        self.bob = bob
        self.offset = bob.position - pivot.position
        self.elastic_limit = elastic_limit
        self.k = spring_constant_k

    def update(self):
        x = self.bob.position - (self.pivot.position + self.offset)
        self.bob.velocity.x += -self.k*x.x
        self.bob.velocity.y += -self.k*x.y
        self.bob.velocity.x *= dampen
        self.bob.velocity.y *= dampen
        x = (self.pivot.position + self.offset) - self.bob.position 
        self.pivot.velocity.x += -self.k*x.x
        self.pivot.velocity.y += -self.k*x.y
        self.pivot.velocity.x *= dampen
        self.pivot.velocity.y *= dampen
        
    def draw(self):
        pygame.draw.line(screen, (RED), (self.pivot.position.x, self.pivot.position.y), (self.bob.position.x, self.bob.position.y))

class Softbody(Particle):
    def __init__(self, x, y, size = particle_size, color = WHITE):
        super().__init__(x, y, size, color)
        self.particles = []
        self.springs = []
    
    def add_spring(self, spring):
            self.springs.append(spring)
            self.particles.append(spring.pivot)
            self.particles.append(spring.bob)

class SoftbodyCircle(Softbody):
    def __init__(self, position, num_particles = 10):
        self.position = Vec2(position.x, position.y)
        self.particles = [Particle(self.position.x, self.position.y, particle_size, RED)]
        self.springs = []

        # Create particles
        angle = 360 / num_particles
        for i in range(num_particles):
            self.particles.append(Particle(self.position.x + (100*math.cos((math.pi*i*angle)/180)), self.position.y + (100*math.sin((math.pi*angle*i)/180)), particle_size, WHITE))
        
        # Create springs
        for i in range(0, len(self.particles)-1):
            self.springs.append(Spring(self.particles[i], self.particles[i+1]))
        # close loop
        self.springs.append(Spring(self.particles[1], self.particles[len(self.particles)-1]))
        # center connection
        for i in range(1, len(self.particles)):
            self.springs.append(Spring(self.particles[i], self.particles[0]))

rope = Softbody(center_x, center_y)
rope.add_spring(Spring(Particle(center_x, center_y), Particle(center_x, center_y + 25)))
for i in range(10):
    rope.add_spring(Spring(rope.springs[i].bob, Particle(center_x, rope.springs[i].bob.position.y + 25)))

rope2 = Softbody(center_x+200, center_y)
rope2.add_spring(Spring(Particle(rope2.position.x, rope2.position.y), Particle(rope2.position.x, rope2.position.y + 15), spring_constant_k=0.01))
for i in range(20):
    rope2.add_spring(Spring(rope2.springs[i].bob, Particle(rope2.springs[i].bob.position.x, rope2.springs[i].bob.position.y + 15), spring_constant_k=0.01))

softbodies = [
    SoftbodyCircle(Vec2(center_x, center_y)),
    SoftbodyCircle(Vec2(0, 0), 36),
    rope,
    rope2
]
grabbing = None
def update():
    global grabbing
    (x, y) = pygame.mouse.get_pos()
    if pygame.mouse.get_pressed()[0]:
        if grabbing == None:
            for body in softbodies:
                for particle in body.particles:
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
        softbodies[0].particles[0].velocity.x -= 10
    if keys[pygame.K_d]:
        softbodies[0].particles[0].velocity.x += 10
    if keys[pygame.K_w]:
        softbodies[0].particles[0].velocity.y -= 10  
    if keys[pygame.K_s]:
        softbodies[0].particles[0].velocity.y += 10

    for body in softbodies:
        body.update()
        for particle in body.particles:
            particle.update()
        for spring in body.springs:
            spring.update()
        

            
def draw():
    # Fill the screen with white
    screen.fill((0,0,0))
    
    for body in softbodies:
        for particle in body.particles:
            particle.draw()
        for spring in body.springs:
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