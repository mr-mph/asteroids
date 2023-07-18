import random
import arcade
import arcade.gui
import math

# --- Constants ---x
SPRITE_SCALING_PLAYER = 1
SPRITE_SCALING_ASTEROID = 2
SPRITE_SCALING_LASER = 0.8
ASTEROID_COUNT = 100
PLAYER_MOVEMENT_SPEED = 10
BULLET_SPEED = 10
ASTEROID_SPEED = 8
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Game"


# TODO: add symbols on screen for player health

class MyWindow(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title, resizable=True)
        self.score = 0
        self.high_score = 0
        self.timer = 0
        bgmusic = arcade.load_sound("Assets/undertalebgmusic.wav")
        arcade.play_sound(bgmusic, looping=True)


class StartView(arcade.View):

    def __init__(self):
        super().__init__()

        # --- Required for all code that uses UI element,
        # a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Set background color
        arcade.set_background_color(arcade.csscolor.SEA_GREEN)

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()
        # Create a text label
        ui_text_label = arcade.gui.UITextArea(text="Falling Asteroids",
                                              width=590,
                                              height=100,
                                              font_size=60, )
        self.v_box.add(ui_text_label.with_space_around(bottom=20))

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

        # Create a UIFlatButton
        ui_flatbutton = arcade.gui.UIFlatButton(text="Play", width=150)
        self.v_box.add(ui_flatbutton.with_space_around(bottom=20))

        # Handle Clicks
        @ui_flatbutton.event("on_click")
        def on_click_flatbutton(event):
            self.manager.disable()
            game_view = GameView()
            game_view.setup()
            self.window.show_view(game_view)

        # Create a UIFlatButton
        ui_flatbutton = arcade.gui.UIFlatButton(text="Instructions", width=150)
        self.v_box.add(ui_flatbutton.with_space_around(bottom=20))

        # Handle Clicks
        @ui_flatbutton.event("on_click")
        def on_click_flatbutton(event):
            self.manager.disable()
            instructions_view = InstructionsView()
            self.window.show_view(instructions_view)

        # Create a UIFlatButton
        ui_flatbutton = arcade.gui.UIFlatButton(text="Quit", width=150)
        self.v_box.add(ui_flatbutton.with_space_around(bottom=20))

        # Handle Clicks
        @ui_flatbutton.event("on_click")
        def on_click_flatbutton(event):
            arcade.exit()

    def on_draw(self):
        self.window.clear()
        self.manager.draw()
        with open("all_time_high_score.txt") as text:
            text = text.read()
            arcade.draw_text(f"All Time Best: {text}", 10,
                             self.window.height - 30, arcade.color.WHITE, 20, 320, "left", "Comfortaa")
        arcade.draw_text(f"Score: {self.window.score}", self.window.width - 170, self.window.height - 30,
                         arcade.color.WHITE, 20, 160, "right", "Comfortaa")


class InstructionsView(arcade.View):

    def on_show(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.SEA_GREEN)

    def on_draw(self):
        """ Draw this view """
        self.window.clear()
        arcade.draw_text("Instructions", self.window.width / 2, self.window.height / 2 + 100,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Shoot as many asteroids as possible without crashing",
                         self.window.width / 2, self.window.height / 2 + 25, arcade.color.WHITE, font_size=22,
                         anchor_x="center")
        arcade.draw_text("Use arrow keys to move and space bar to shoot", self.window.width / 2,
                         self.window.height / 2 - 25, arcade.color.WHITE, font_size=22, anchor_x="center")
        arcade.draw_text("Click to go back", self.window.width / 2,
                         self.window.height / 2 - 75, arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, go back to the main menu. """
        start_view = StartView()
        self.window.show_view(start_view)


class Asteroid(arcade.Sprite):

    def __int__(self):
        self.movement_angle = 0

    def update(self):
        # Move the asteroid using angle

        # Convert angle in degrees to radians.
        angle_rad = math.radians(self.movement_angle)

        # Rotate the asteroid
        self.angle += self.change_angle

        # Use math to find our change based on our speed and angle
        self.center_x -= ASTEROID_SPEED * math.sin(angle_rad) * (1 + (arcade.get_window().timer / 100))
        self.center_y += ASTEROID_SPEED * math.cos(angle_rad) * (1 + (arcade.get_window().timer / 100))

        # See if the asteroid has fallen off the bottom of the screen.
        # If so, remove it.
        if self.top < 0:
            self.remove_from_sprite_lists()


class GameView(arcade.View):

    def __init__(self):

        # Call the parent class initializer
        super().__init__()

        # Variables that will hold sprite lists
        self.player_sprite_list = None
        self.asteroid_sprite_list = None
        self.bullet_list = None

        # Sounds
        self.gun_sound = arcade.load_sound(":resources:sounds/hurt5.wav")
        self.hit_sound = arcade.load_sound(":resources:sounds/hit5.wav")
        self.die_sound = arcade.load_sound(":resources:sounds/explosion2.wav")

        # Set up the player info
        self.player_sprite = None
        self.lives = 3
        self.left_pressed = False
        self.right_pressed = False
        self.timing_helper_asteroids = 0
        self.timing_helper_bullets = 0
        self.player_hit_animation = 0
        self.bullets_on = False
        self.old_asteroid_center_x = self.window.width / 2

        arcade.set_background_color(arcade.color.SMOKY_BLACK)

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.player_sprite_list = arcade.SpriteList()
        self.asteroid_sprite_list = arcade.SpriteList()
        self.bullet_list = arcade.SpriteList()

        # Score
        self.lives = 3
        self.window.timer = 0
        self.window.score = 0

        # Set up the player
        # Character image from kenney.nl
        self.player_sprite = arcade.Sprite(":resources:images/space_shooter/playerShip1_blue.png",
                                           SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = self.window.width / 2
        self.player_sprite.center_y = 50
        self.player_sprite_list.append(self.player_sprite)
        self.bullets_on = False

    def on_draw(self):
        """ Draw everything """
        self.window.clear()
        self.asteroid_sprite_list.draw()
        self.player_sprite_list.draw()
        self.bullet_list.draw()

        # Put the text on the screen.

        arcade.draw_text(f"Lives: {self.lives}", 10, self.window.height - 30, arcade.color.WHITE, 20, 0, "left",
                         "Comfortaa")

        arcade.draw_text(f"Score: {self.window.score}", self.window.width - 170, self.window.height - 30,
                         arcade.color.WHITE, 20, 160, "right", "Comfortaa")

    def update_player_speed(self):

        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0

        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_update(self, delta_time):
        """ Movement and game logic """

        global ASTEROID_SPEED
        if self.player_sprite.left < 0:
            self.player_sprite.left = 0
        if self.player_sprite.right > self.window.width:
            self.player_sprite.right = self.window.width

        # Spawn asteroids
        if self.timing_helper_asteroids > 1:
            # Create the asteroid instance
            asteroid = Asteroid(f":resources:images/space_shooter/meteorGrey_big{random.randrange(1, 4)}.png",
                                SPRITE_SCALING_ASTEROID, angle=random.randrange(0, 360))
            asteroid.movement_angle = random.randrange(135, 225)
            asteroid.state = "large"
            # Position the asteroid
            asteroid.center_x = random.randrange(50, self.window.width - 50)
            while abs(asteroid.center_x - self.old_asteroid_center_x) < 100:
                asteroid.center_x = random.randrange(50, self.window.width - 50)

            self.old_asteroid_center_x = asteroid.center_x

            asteroid.bottom = self.window.height

            # Add the asteroid to the lists
            self.asteroid_sprite_list.append(asteroid)

            self.timing_helper_asteroids = 0

        else:
            self.timing_helper_asteroids += delta_time * self.window.width / 200

        # Generate a list of all asteroids that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.asteroid_sprite_list)

        # Loop through each colliding asteroid, remove it, and remove from the lives.
        for asteroid in hit_list:
            if self.player_hit_animation <= 0:
                asteroid.remove_from_sprite_lists()
                self.lives -= 1
                self.player_hit_animation = 1
                arcade.play_sound(self.die_sound)

        if self.lives <= 0:
            view = StartView()
            self.window.show_view(view)

        if self.bullets_on and self.timing_helper_bullets > 1:
            # Gunshot sound
            arcade.play_sound(self.gun_sound, 0.5)
            # Create a bullet
            bullet = arcade.Sprite(":resources:images/space_shooter/laserBlue01.png", SPRITE_SCALING_LASER, angle=90)

            # Give the bullet a speed
            bullet.change_y = BULLET_SPEED

            # Position the bullet
            bullet.center_x = self.player_sprite.center_x
            bullet.bottom = self.player_sprite.top - 10

            # Add the bullet to the appropriate lists
            self.bullet_list.append(bullet)

            self.timing_helper_bullets = 0
        else:
            self.timing_helper_bullets += delta_time * 6

        if self.player_hit_animation > 0:
            self.player_hit_animation -= delta_time
            self.player_sprite.alpha = 50
        else:
            self.player_sprite.alpha = 255

        # Loop through each bullet
        for bullet in self.bullet_list:

            # Check this bullet to see if it hit an asteroid
            hit_list = arcade.check_for_collision_with_list(bullet, self.asteroid_sprite_list)

            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # For every asteroid we hit, add to the score and remove the asteroid
            for asteroid in hit_list:
                if asteroid.state == "large":
                    # Create smaller asteroids
                    mini_asteroid = Asteroid(
                        f":resources:images/space_shooter/meteorGrey_big{random.randrange(1, 4)}.png",
                        SPRITE_SCALING_ASTEROID / 2, angle=random.randrange(0, 360),
                        center_x=asteroid.center_x + random.randrange(0, 50),
                        center_y=asteroid.center_y + random.randrange(0, 50))
                    mini_asteroid.state = "small"
                    mini_asteroid.movement_angle = random.randrange(90, 270)
                    self.asteroid_sprite_list.append(mini_asteroid)
                    mini_asteroid = Asteroid(
                        f":resources:images/space_shooter/meteorGrey_big{random.randrange(1, 4)}.png",
                        SPRITE_SCALING_ASTEROID / 2, angle=random.randrange(0, 360),
                        center_x=asteroid.center_x + random.randrange(0, 50),
                        center_y=asteroid.center_y - random.randrange(0, 50))
                    mini_asteroid.state = "small"
                    mini_asteroid.movement_angle = random.randrange(90, 270)
                    self.asteroid_sprite_list.append(mini_asteroid)
                    mini_asteroid = Asteroid(
                        f":resources:images/space_shooter/meteorGrey_big{random.randrange(1, 4)}.png",
                        SPRITE_SCALING_ASTEROID / 2, angle=random.randrange(0, 360),
                        center_x=asteroid.center_x - random.randrange(0, 50),
                        center_y=asteroid.center_y + random.randrange(0, 50))
                    mini_asteroid.state = "small"
                    self.asteroid_sprite_list.append(mini_asteroid)
                    mini_asteroid.movement_angle = random.randrange(90, 270)
                    mini_asteroid = Asteroid(
                        f":resources:images/space_shooter/meteorGrey_big{random.randrange(1, 4)}.png",
                        SPRITE_SCALING_ASTEROID / 2, angle=random.randrange(0, 360),
                        center_x=asteroid.center_x - random.randrange(0, 50),
                        center_y=asteroid.center_y - random.randrange(0, 50))
                    mini_asteroid.state = "small"
                    mini_asteroid.movement_angle = random.randrange(90, 270)
                    self.asteroid_sprite_list.append(mini_asteroid)

                    asteroid.remove_from_sprite_lists()
                    self.window.score += 10
                else:
                    asteroid.remove_from_sprite_lists()
                    self.window.score += 5
                # Hit Sound
                arcade.play_sound(self.hit_sound)

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > self.window.height:
                bullet.remove_from_sprite_lists()

        # Update the high score
        if self.window.score > self.window.high_score:
            self.window.high_score = self.window.score
            with open("all_time_high_score.txt", "r") as text_r:
                if self.window.high_score > int(text_r.read()):
                    with open("all_time_high_score.txt", "w") as text_w:
                        text_w.write(str(self.window.high_score))

        # Call update on all sprites
        self.asteroid_sprite_list.update()
        self.player_sprite_list.update()
        self.bullet_list.update()

        # Update timer
        self.window.timer += delta_time

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.LEFT:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.RIGHT:
            self.right_pressed = True
            self.update_player_speed()
        if key == arcade.key.SPACE:
            self.bullets_on = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.LEFT:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.RIGHT:
            self.right_pressed = False
            self.update_player_speed()
        if key == arcade.key.SPACE:
            self.bullets_on = False


def main():
    window = MyWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = StartView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
