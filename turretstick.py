import pygame
from WaterTurret import WaterTurret


turret = WaterTurret(Port='/dev/rfcomm1')

turret.off()


turretEnable = False

# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')


# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.
class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10



pygame.init()


# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((500, 700))

pygame.display.set_caption("My Game")



# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Initialize the joysticks.
pygame.joystick.init()


# Get ready to print.
textPrint = TextPrint()



done = False

# -------- Main Program Loop -----------
while not done:
    #
    # EVENT PROCESSING STEP
    #
    # Possible joystick actions: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
    # JOYBUTTONUP, JOYHATMOTION
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
        elif event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")

    screen.fill(WHITE)
    textPrint.reset()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()

    if joystick.get_button(2):
       turret.off()
       turretEnable=False
    elif joystick.get_button(3):
       turretEnable=True


    if turretEnable:
      valuex = joystick.get_axis(0) * 90 + 90
      valuey = joystick.get_axis(1) * 90 + 90
      pump = joystick.get_button(0)

      textPrint.indent()
      textPrint.tprint(screen, "Axis X value: {:>6.3f}".format(valuex))
#      textPrint.unindent()
      textPrint.tprint(screen, "Axis Y value: {:>6.3f}".format(valuey))
#      textPrint.unindent()
      textPrint.tprint(screen, "Pump   value: {}".format(pump))
#      textPrint.unindent()
      textPrint.unindent()

      turret.xy(int(valuex),int(valuey))
      turret.pump(pump)




    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    #

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second.
    clock.tick(20)





# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()
turret.off()

