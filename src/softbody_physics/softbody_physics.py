import pygame
import math
from typing import Tuple, List, Optional

class Vec2:
    def __init__(self, x: float = 0, y: float = 0):
        self.x: float = x
        self.y: float = y

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)
    
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)
    
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

def clamp(value: float, min: float, max: float) -> float:
    if value < min:
        value = min
    elif value > max:
        value = max
    return value

dampen: float = 0.99
class Particle:
    default_particle_size: int = 15
    s_particles: List[object] = []
    def __init__(self, x: float, y: float, particle_size: int = default_particle_size, color = BLUE):
        self.position: Vec2 = Vec2(x, y)
        self.particle_size: int = particle_size
        self.radius: float = particle_size/2
        self.color = color
        self.speed: float = 10
        self.velocity: Vec2 = Vec2(0, 0)
        Particle.s_particles.append(self)

    def update(self) -> None:
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y

    def draw(self, screen) -> None:
        pygame.draw.circle(screen, self.color, (self.position.x, self.position.y), self.radius)
        
    def rect(self) -> object:
        return pygame.Rect(self.position.x-self.radius, self.position.y-self.radius, self.radius*2, self.radius*2)
    
class Spring:
    s_springs: List[object] = []
    def __init__(self, pivot: Vec2, bob: Vec2, spring_constant_k: float = 0.01, color = WHITE):
        self.color = color
        self.pivot: Vec2 = pivot
        self.bob: Vec2 = bob
        self.offset: Vec2 = bob.position - pivot.position
        self.k: float = spring_constant_k
        Spring.s_springs.append(self)

    def update(self) -> None:
        x: Vec2 = self.bob.position - (self.pivot.position + self.offset)
        self.bob.velocity.x += -self.k*x.x
        self.bob.velocity.y += -self.k*x.y
        self.bob.velocity.x *= dampen
        self.bob.velocity.y *= dampen
        x = (self.pivot.position + self.offset) - self.bob.position 
        self.pivot.velocity.x += -self.k*x.x
        self.pivot.velocity.y += -self.k*x.y
        self.pivot.velocity.x *= dampen
        self.pivot.velocity.y *= dampen
        
    def draw(self, screen) -> None:
        pygame.draw.line(screen, (self.color), (self.pivot.position.x, self.pivot.position.y), (self.bob.position.x, self.bob.position.y))

class Softbody:
    def __init__(self, x: float, y: float, particle_size: int = Particle.default_particle_size, spring_constant_k: float = 0.01, color = BLUE):
        self.position = Vec2(x, y)
        self.particle_size: int = particle_size
        self.k: float = spring_constant_k
        self.color = color
        self.particles: List[Particle] = []
        self.springs: List[Spring] = []

    def add_spring(self, spring: Spring) -> None:
            self.springs.append(spring)
            self.particles.append(spring.pivot)
            self.particles.append(spring.bob)
    
    def update(self) -> None:
        for spring in self.springs:
            spring.update()
        for particle in self.particles:
            particle.update()

    def draw(self, screen) -> None:
        for spring in self.springs:
            spring.draw(screen)
        for particle in self.particles:
            particle.draw(screen)

class SoftbodyCircle(Softbody):
    def __init__(self, position: Vec2, radius: float = 75, num_particles: int = 10, spring_constant_k: float = 0.01, particle_size: int = Particle.default_particle_size, color = BLUE, exclude_center: bool = False):
        super().__init__(position.x, position.y, particle_size, spring_constant_k, color)

        if not exclude_center:
            self.particles.append(Particle(self.position.x, self.position.y, particle_size, self.color))

        # Create particles
        angle: float = 360 / num_particles
        for i in range(num_particles):
            self.particles.append(Particle(self.position.x + (radius*math.cos((math.pi*i*angle)/180)), self.position.y + (radius*math.sin((math.pi*angle*i)/180)), self.particle_size, self.color))
        
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

class SoftbodySquare(Softbody):
    def __init__(self, x: int, y: int, width: float, height: float, particle_size: int = Particle.default_particle_size, density: int = 4, spring_constant_k: float = 0.01, color = BLUE):
        super().__init__(x, y, particle_size, spring_constant_k, color)
        
        top_left: Particle = Particle(x-(width/2), y-(height/2), self.particle_size, color)
        top_right: Particle = Particle(x+(width/2), y-(height/2), self.particle_size, color)
        bottom_right: Particle = Particle(x+(width/2), y+(height/2), self.particle_size, color)
        bottom_left: Particle = Particle(x-(width/2), y+(height/2), self.particle_size, color)
        
        offset: float = width/(density)
        prev: Particle = None
        for i in range(0, density):
            if prev == None:
                prev = top_left
                self.particles.append(top_left)
            current: Particle = Particle(prev.position.x + offset, prev.position.y)
            self.particles.append(current)
            self.springs.append(Spring(prev, current, spring_constant_k))
            prev = current

        for i in range(0, density):
            current: Particle = Particle(prev.position.x, prev.position.y + offset)
            self.particles.append(current)
            self.springs.append(Spring(prev, current, spring_constant_k))
            prev = current

        for i in range(0, density):
            current: Particle = Particle(prev.position.x-offset, prev.position.y)
            self.particles.append(current)
            self.springs.append(Spring(prev, current, spring_constant_k))
            prev = current

        for i in range(0, density-1):
            current: Particle = Particle(prev.position.x, prev.position.y-offset)
            self.particles.append(current)
            self.springs.append(Spring(prev, current, spring_constant_k))
            prev = current

        # close loop
        self.springs.append(Spring(prev, self.particles[0], spring_constant_k))

class Cloth(Softbody):
    def __init__(self, position: Vec2, width: float, height: float, density: int = 10, spring_constant_k: float = 0.01, particle_size: int = Particle.default_particle_size, color=WHITE):
        super().__init__(position.x, position.y, particle_size, spring_constant_k, color)
        self.width: float = width
        self.height: float = height
        self.density: int = density
        self.mtx: List[List[float]] = []
        for i in range(density):
            self.mtx.append([None for p in range(density)])

        for r in range(density):
            vert_offset: float = r * (height/density)
            for c in range(density):
                horiz_offset: float = c*(width/density)
                self.mtx[r][c] = Particle(self.position.x + horiz_offset, self.position.y + vert_offset, self.particle_size, color=self.color)

        for r in range(self.density):
            for c in range(self.density):
                if r != self.density-1:
                    # Connect adjacent row
                    pivot: Vec2 = self.mtx[r][c]
                    bob: Vec2 = self.mtx[r+1][c]
                    self.springs.append(Spring(pivot, bob, spring_constant_k))
                    self.particles.append(pivot)
                    self.particles.append(bob)
                if c != self.density-1:
                    # Connect adjacent column
                    pivot: Vec2 = self.mtx[r][c]
                    bob: Vec2 = self.mtx[r][c+1]
                    self.springs.append(Spring(pivot, bob, spring_constant_k))
                    self.particles.append(pivot)
                    self.particles.append(bob)

def create_rope(position: Vec2, n_particles: int, k: float) -> Softbody:
    rope: Softbody = Softbody(position[0], position[1], particle_size=Particle.default_particle_size, spring_constant_k=k)
    for i in range(n_particles):
        if i == 0:
            rope.add_spring(Spring(Particle(rope.position.x, rope.position.y), Particle(rope.position.x, rope.position.y + 15), spring_constant_k=k))
        rope.add_spring(Spring(rope.springs[i].bob, Particle(rope.springs[i].bob.position.x, rope.springs[i].bob.position.y + 15), spring_constant_k=k))
    return rope

if __name__ == "__main__":
    pygame.init()
    screen_width: int = 800
    screen_height: int = 800
    # Set up the display.
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Softbody Physics")
    title = pygame.font.SysFont("Arial", 30)
    font = pygame.font.SysFont('Arial', 20)
    center_x: float = screen_width / 2
    center_y: float = screen_height / 2
    origin: Vec2 = Vec2(center_x, center_y)

    mouse_pressed: bool = False
    prevGrabbing: bool = None   
    grabbing: Tuple[Softbody, Particle] = None

    softbodies: List[Softbody] = [
        # SoftbodyCircle(Vec2(center_x-200, center_y-200), spring_constant_k = 0.3, exclude_center=True), 
        # SoftbodyCircle(Vec2(center_x, center_y-200), spring_constant_k = 0.3), 
        # SoftbodyCircle(Vec2(center_x-200, center_y+10), num_particles=17, spring_constant_k=0.1),
        # SoftbodyCircle(Vec2(center_x, center_y+10), num_particles=36, spring_constant_k = 0.1),
        # SoftbodyCircle(Vec2(center_x-200, center_y+200), num_particles=17, spring_constant_k=0.01),
        # SoftbodyCircle(Vec2(center_x, center_y+200), num_particles=36, spring_constant_k = 0.01),
        # SoftbodySquare(center_x, center_x, 200, 200, spring_constant_k=.15 , density=3),
        # create_rope((center_x+100, center_y), 20, 0.1),
        # create_rope((center_x+200, center_y), 20, 0.01),
        Cloth(origin-Vec2(200, 200), 400, 400, 20, particle_size=10, color=WHITE)
    ]

    springs: List[Spring] = [
        Spring(Particle(center_x+300, center_y, 25), Particle(center_x+300, center_y, 25)),
        Spring(Particle(center_x+350, center_y, 25), Particle(center_x+350, center_y+100, 25)),
    ]

    # alpha not ready
    def collision_physics() -> None:
        for particle in Particle.s_particles:
            rect = pygame.Rect(particle.position.x, particle.position.y, particle.radius*2, particle.radius*2)        
            for other in Particle.s_particles:
                if other != particle:
                    otherRect = pygame.Rect(other.position.x, other.position.y, other.radius*2, other.radius*2)
                    if rect.colliderect(otherRect):
                        x_offest = (other.position.x - particle.position.x) / 10.0
                        y_offest = (other.position.y - particle.position.y) / 10.0
                        other.position.x += x_offest
                        other.position.y += y_offest
                        particle.position.x -= x_offest
                        particle.position.y -= y_offest
                        temp_vel_x = other.velocity.x
                        temp_vel_y = other.velocity.y
                        other.velocity.x = particle.velocity.x
                        other.velocity.y = particle.velocity.y
                        particle.velocity.x = temp_vel_x
                        particle.velocity.y = temp_vel_y

    def update() -> None:
        for spring in Spring.s_springs:
            spring.update()

        for particle in Particle.s_particles:
            particle.update()
            
    def draw() -> None:
        global prevGrabbing

        screen.fill((0,0,0))
            
        for spring in Spring.s_springs:
            spring.draw(screen)

        for particle in Particle.s_particles:
            particle.draw(screen)

        screen.blit(title.render(f"Spring Force = -kx", True, WHITE), (20, 20))
        screen.blit(title.render(f"Softbody Physics", True, WHITE), (center_x-100, 20))
        if grabbing and grabbing[0]:
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

    # The game loop
    running: bool = True
    while running:
        (mouse_x, mouse_y) = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed = True
                if grabbing == None:
                    for particle in Particle.s_particles:
                        if particle.rect().collidepoint(mouse_x, mouse_y):
                            grabbing = (None, particle)
                            for body in softbodies:
                                if particle in body.particles:
                                    grabbing = (body, particle)
                                    break
            elif event.type == pygame.MOUSEBUTTONUP:
                grabbing = None
                mouse_pressed = False
        if mouse_pressed and grabbing:
            grabbing[1].position.x = mouse_x
            grabbing[1].position.y = mouse_y
            grabbing[1].velocity.x = 0
            grabbing[1].velocity.y = 0
        #collision_physics() # alpha not ready
        update()
        draw()
        # Control the frame rate
        pygame.time.Clock().tick(60)

    pygame.quit()