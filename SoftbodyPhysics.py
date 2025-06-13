import pygame
import random
import math
import time
pygame.init()
title = pygame.font.SysFont("Arial", 30)
font = pygame.font.SysFont('Arial', 20)

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
pygame.display.set_caption("Softbody Physics")
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

dampen = 0.99
particle_size = 10
class Particle:
    position = Vec2()
    velocity = Vec2()
    width = 10
    height = 10
    radius = 10
    color = WHITE
    speed = 10

    def __init__(self, x, y, size = particle_size, color = BLUE):
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
    def __init__(self, pivot, bob, spring_constant_k = 0.01):
        self.pivot = pivot
        self.bob = bob
        self.offset = bob.position - pivot.position
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
        pygame.draw.line(screen, (BLUE), (self.pivot.position.x, self.pivot.position.y), (self.bob.position.x, self.bob.position.y))

class Softbody(Particle):
    def __init__(self, x, y, size = particle_size, spring_constant_k = 0.01, color = BLUE):
        super().__init__(x, y, size, color)
        self.particles = []
        self.springs = []
        self.k = spring_constant_k

    def add_spring(self, spring):
            self.springs.append(spring)
            self.particles.append(spring.pivot)
            self.particles.append(spring.bob)

class SoftbodyCircle(Softbody):
    def __init__(self, position, radius = 75, num_particles = 10, spring_constant_k = 0.01, exclude_center = False):
        self.position = Vec2(position.x, position.y)
        self.k = spring_constant_k
        self.particles = []
        self.springs = []

        if not exclude_center:
            self.particles.append(Particle(self.position.x, self.position.y, particle_size, self.color))

        # Create particles
        angle = 360 / num_particles
        for i in range(num_particles):
            self.particles.append(Particle(self.position.x + (radius*math.cos((math.pi*i*angle)/180)), self.position.y + (radius*math.sin((math.pi*angle*i)/180)), particle_size, self.color))
        
        # Create springs
        for i in range(0, len(self.particles)-1):
            self.springs.append(Spring(self.particles[i], self.particles[i+1], spring_constant_k=self.k))
        # close loop
        if exclude_center:
            self.springs.append(Spring(self.particles[0], self.particles[len(self.particles)-1], spring_constant_k=self.k))
        else:
            self.springs.append(Spring(self.particles[1], self.particles[len(self.particles)-1], spring_constant_k=self.k))
        if not exclude_center:
            # center connection
            for i in range(1, len(self.particles)):
                self.springs.append(Spring(self.particles[i], self.particles[0], spring_constant_k=self.k))

class Cloth(Softbody):
    def __init__(self, position, width, height, spring_constant_k = 0.01):
        super().__init__(position.x, position.y)
        self.particles = []
        self.springs = []
        self.k = spring_constant_k
        self.position = position
        spacing = 15
        cols = []
        rows = []
        cols.append(Spring(Particle(self.position.x, self.position.y), Particle(self.position.x + spacing, self.position.y), spring_constant_k=self.k))
        for r in range(height):
            for c in range(width):
                spring = (Spring(cols[c].bob, Particle(cols[c].bob.position.x + spacing, cols[c].bob.position.y + (r*spacing)), spring_constant_k=self.k))
                cols.append(spring)
                self.add_spring(spring)

def create_rope(position, n_particles, k):
    rope = Softbody(position[0], position[1], spring_constant_k=k)
    for i in range(n_particles):
        if i == 0:
            rope.add_spring(Spring(Particle(rope.position.x, rope.position.y), Particle(rope.position.x, rope.position.y + 15), spring_constant_k=k))
        rope.add_spring(Spring(rope.springs[i].bob, Particle(rope.springs[i].bob.position.x, rope.springs[i].bob.position.y + 15), spring_constant_k=k))
    return rope

cloth = Cloth(origin, 5, 5, 0.001)

softbodies = [
    SoftbodyCircle(Vec2(center_x-200, center_y-200), spring_constant_k = 0.3, exclude_center=True), 
    SoftbodyCircle(Vec2(center_x, center_y-200), spring_constant_k = 0.3), 
    SoftbodyCircle(Vec2(center_x-200, center_y+10), num_particles=17, spring_constant_k=0.1),
    SoftbodyCircle(Vec2(center_x, center_y+10), num_particles=36, spring_constant_k = 0.1),
    SoftbodyCircle(Vec2(center_x-200, center_y+200), num_particles=17, spring_constant_k=0.01),
    SoftbodyCircle(Vec2(center_x, center_y+200), num_particles=36, spring_constant_k = 0.01),
    create_rope((center_x+100, center_y), 20, 0.1),
    create_rope((center_x+200, center_y), 20, 0.01),
    #cloth
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
                        grabbing = [body, particle]
        else:
            grabbing[1].position.x = x
            grabbing[1].position.y = y
            grabbing[1].velocity.x = 0
            grabbing[1].velocity.y = 0

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
        


prevGrabbing = None            
def draw():
    global prevGrabbing
    # Fill the screen with white
    screen.fill((0,0,0))
    
    for body in softbodies:
        for particle in body.particles:
            particle.draw()
        for spring in body.springs:
            spring.draw()

    screen.blit(title.render(f"Spring Force = -kx", True, WHITE), (20, 20))
    screen.blit(title.render(f"Softbody Physics", True, WHITE), (center_x-100, 20))
    if grabbing:
        prevGrabbing = grabbing
        screen.blit(font.render(f"Spring Constant k = {grabbing[0].k}", True, RED), (20, 70))
        screen.blit(font.render(f"Springs: {len(grabbing[0].springs)}", True, RED), (20, 100))
    elif prevGrabbing:
        screen.blit(font.render(f"Spring Constant k = {prevGrabbing[0].k}", True, (150, 150, 150)), (20, 70))
        screen.blit(font.render(f"Springs: {len(prevGrabbing[0].springs)}", True, (150, 150, 150)), (20, 100))
    else:
        screen.blit(font.render("Spring Constant k =", True, (100, 100, 100)), (20, 70))
        screen.blit(font.render(f"Springs: ", True, (100, 100, 100)), (20, 100))

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