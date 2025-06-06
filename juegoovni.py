import pygame
import random
import sys

# ------------------- FUNCIONES PARA PUNTAJE MÁXIMO -------------------
def cargar_puntaje_maximo():
    try:
        with open("puntaje_maximo.txt", "r") as archivo:
            return int(archivo.read())
    except:
        return 0  # Si el archivo no existe o está vacío

def guardar_puntaje_maximo(nuevo_puntaje):
    with open("puntaje_maximo.txt", "w") as archivo:
        archivo.write(str(nuevo_puntaje))

# ----------------------------------------------------------------------

# Inicializar pygame
pygame.init()

# Constantes de pantalla
WIDTH, HEIGHT = 700, 700
FPS = 60
GRAVEDAD = 0.5
FUERZA_SALTO = -10

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
ROSA = (255, 192, 220)

# Pantalla
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ovni Esquiva Tubos cande anto")
clock = pygame.time.Clock()

# Fuente
fuente = pygame.font.SysFont(None, 36)

# Cargar imágenes
ovni_img = pygame.image.load("OVNI-removebg-preview.png").convert_alpha()
ovni_img = pygame.transform.scale(ovni_img, (120, 90))

explosion_img = pygame.image.load("EXPLOROSA-removebg-preview.png").convert_alpha()
explosion_img = pygame.transform.scale(explosion_img, (300, 300))

tubo_img = pygame.Surface((80, HEIGHT), pygame.SRCALPHA)
pygame.draw.rect(tubo_img, ROSA, [1, 0, 80, HEIGHT])

moneda_img = pygame.image.load("MONEDA-removebg-preview(1).png").convert_alpha()
moneda_img = pygame.transform.scale(moneda_img, (50, 50))


# Clase Ovni
class Ovni(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ovni_img
        self.rect = self.image.get_rect(center=(100, HEIGHT // 2))
        self.vel_y = 0
        self.vidas = 3
        self.explotado = False

    def update(self):
        if not self.explotado:
            self.vel_y += GRAVEDAD
            self.rect.y += self.vel_y

            if self.rect.top <= 0:
                self.rect.top = 0
            if self.rect.bottom >= HEIGHT:
                self.rect.bottom = HEIGHT
                self.vel_y = 0

    def saltar(self):
        if not self.explotado:
            self.vel_y = FUERZA_SALTO

    def explotar(self):
        self.image = explosion_img
        self.explotado = True


# Clase Tubo
class Tubo(pygame.sprite.Sprite):
    def __init__(self, x, altura, es_superior):
        super().__init__()
        self.image = tubo_img
        self.rect = self.image.get_rect()
        if es_superior:
            self.image = pygame.transform.flip(tubo_img, False, True)
            self.rect.bottomleft = (x, altura - 100)
        else:
            self.rect.topleft = (x, altura + 100)
        self.velocidad = 4

    def update(self):
        self.rect.x -= self.velocidad
        if self.rect.right < 0:
            self.kill()


# Clase Moneda
class Moneda(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = moneda_img
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 4

    def update(self):
        self.rect.x -= self.velocidad
        if self.rect.right < 0:
            self.kill()


# Crear objetos
ovni = Ovni()
grupo_ovni = pygame.sprite.GroupSingle(ovni)
grupo_tubos = pygame.sprite.Group()
grupo_monedas = pygame.sprite.Group()

# Variables de juego
puntaje = 0
puntaje_maximo = cargar_puntaje_maximo()
contador_tubos = 0
juego_terminado = False
tiempo_explosion = 0

# Loop principal
running = True
while running:
    clock.tick(FPS)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not juego_terminado:
                ovni.saltar()

    if not juego_terminado:
        # Generar tubos y monedas cada 90 cuadros
        contador_tubos += 1
        if contador_tubos >= 90:
            altura = random.randint(150, HEIGHT - 150)
            grupo_tubos.add(Tubo(WIDTH, altura, True))
            grupo_tubos.add(Tubo(WIDTH, altura, False))
            grupo_monedas.add(Moneda(WIDTH + 40, altura))
            contador_tubos = 0

        # Actualizar sprites
        grupo_ovni.update()
        grupo_tubos.update()
        grupo_monedas.update()

        # Colisiones con tubos
        if pygame.sprite.spritecollide(ovni, grupo_tubos, True):
            ovni.vidas -= 1
            if ovni.vidas <= 0:
                ovni.explotar()
                juego_terminado = True
                tiempo_explosion = pygame.time.get_ticks()

        # Colisiones con monedas
        monedas_capturadas = pygame.sprite.spritecollide(ovni, grupo_monedas, True)
        puntaje += len(monedas_capturadas)

    else:
        # Esperar 2 segundos después de explosión y luego cerrar
        if pygame.time.get_ticks() - tiempo_explosion > 2000:
            # Guardar nuevo puntaje máximo si es necesario
            if puntaje > puntaje_maximo:
                guardar_puntaje_maximo(puntaje)
                puntaje_maximo = puntaje
            running = False

    # Dibujar
    screen.fill(BLACK)
    grupo_ovni.draw(screen)
    grupo_tubos.draw(screen)
    grupo_monedas.draw(screen)

    texto_puntaje = fuente.render(f"Puntaje: {puntaje}", True, WHITE)
    texto_vidas = fuente.render(f"Vidas: {ovni.vidas}", True, WHITE)
    texto_maximo = fuente.render(f"Puntaje Máximo: {puntaje_maximo}", True,  WHITE)
    screen.blit(texto_puntaje, (10, 10))
    screen.blit(texto_vidas, (10, 50))
    screen.blit(texto_maximo, (10, 90))

    pygame.display.flip()

# Finalizar
pygame.quit()
sys.exit()
